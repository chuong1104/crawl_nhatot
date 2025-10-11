import asyncio
import re
import pandas as pd
from base_scraper import BaseScraper

class OtoComVnScraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.input_file = "car_detail_urls.txt" # File chứa URL đầu vào
        self.concurrent_scrapes = 15 # Số lượng URL cào đồng thời

    def extract_ad_id_from_url(self, url):
        """Trích xuất mã bản tin từ URL"""
        match = re.search(r'aidxc(\d+)', url)
        return match.group(1) if match else None

    async def process_single_url(self, context, car_url, idx, total_links, semaphore):
        """Worker để xử lý một URL duy nhất, tối ưu hóa tốc độ."""
        async with semaphore:
            new_page = None
            try:
                print(f"Bắt đầu xử lý xe {idx + 1}/{total_links}: {car_url}")
                new_page = await context.new_page()

                block_resource_types = ['stylesheet', 'image', 'font', 'media']
                await new_page.route("**/*", 
                    lambda route: route.abort() if route.request.resource_type in block_resource_types else route.continue_()
                )

                max_retries = 3
                for retry in range(max_retries):
                    try:
                        await new_page.goto(car_url, timeout=45000, wait_until='domcontentloaded')
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            print(f"  -> Lỗi: Không thể tải trang sau {max_retries} lần thử: {car_url}")
                            return None
                        await asyncio.sleep(2 * (retry + 1))

                car_info = await self.extract_car_detail(new_page)
                car_info['url'] = car_url
                print(f"  -> Đã trích xuất: {car_info.get('title', 'N/A')}")
                return car_info
            except Exception as e:
                print(f"  -> Lỗi nghiêm trọng khi xử lý {car_url}: {e}")
                return None
            finally:
                if new_page:
                    await new_page.close()

    async def extract_data_from_links(self, context, car_links):
        """Trích xuất dữ liệu song song từ danh sách link xe."""
        if not car_links:
            print("Không có URL nào để xử lý.")
            return

        total_links = len(car_links)
        print(f"Bắt đầu trích xuất song song từ {total_links} xe với {self.concurrent_scrapes} worker...")

        semaphore = asyncio.Semaphore(self.concurrent_scrapes)
        tasks = [self.process_single_url(context, car_url, idx, total_links, semaphore) for idx, car_url in enumerate(car_links)]
        
        results = await asyncio.gather(*tasks)

        successful_results = [res for res in results if res is not None]
        self.data.extend(successful_results)
        
        print(f"\nHoàn tất xử lý song song. Thành công: {len(successful_results)}/{total_links}.")

        if self.data:
            await self.save_partial_data("batch_final")

    async def extract_car_detail(self, page):
        """Trích xuất thông tin chi tiết của xe từ trang chi tiết (dữ liệu thô)."""
        car_info = {}
        current_url = page.url
        car_info['ad_id'] = self.extract_ad_id_from_url(current_url) or 'N/A'

        # Lấy tiêu đề
        title_elem = await page.query_selector(self.config.TITLE_SELECTORS[0])
        car_info['title'] = (await title_elem.text_content()).strip() if title_elem else 'N/A'

        # Lấy giá (dạng thô)
        price_elem = await page.query_selector(self.config.PRICE_SELECTORS[0])
        car_info['price'] = (await price_elem.text_content()).strip() if price_elem else 'N/A'

        # Lấy ngày đăng (dạng thô)
        date_elem = await page.query_selector(self.config.DATE_POSTED_SELECTORS[0])
        car_info['date_posted'] = (await date_elem.text_content()).strip() if date_elem else 'N/A'

        # Lấy các thông tin chi tiết khác (dạng thô)
        for key, selector in self.config.DETAIL_SELECTORS.items():
            elem = await page.query_selector(selector)
            if elem:
                # Lấy toàn bộ text_content của thẻ li, sau đó loại bỏ nhãn ở đầu
                full_text = await elem.text_content()
                # Tách văn bản bằng ký tự xuống dòng hoặc dấu hai chấm để lấy giá trị
                parts = re.split(r':|\n', full_text, maxsplit=1)
                value = parts[-1].strip() if len(parts) > 1 else full_text.strip()
                car_info[key] = value if value else 'N/A'
            else:
                car_info[key] = 'N/A'

        return car_info

    async def scrape(self):
        """Ghi đè phương thức scrape để đọc URL từ file và cào dữ liệu song song."""
        print(f"Bắt đầu scraping dữ liệu từ file {self.input_file}...")
        try:
            # Đọc file .txt, mỗi dòng là một URL
            with open(self.input_file, 'r', encoding='utf-8') as f:
                car_links = [line.strip() for line in f if line.strip()]
            # Loại bỏ các URL trùng lặp
            car_links = sorted(list(set(car_links)))
            print(f"Tìm thấy {len(car_links)} URL duy nhất để cào.")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {self.input_file}. Hãy chạy script để thu thập URL chi tiết trước.")
            return
        except Exception as e:
            print(f"Lỗi khi đọc file: {e}")
            return

        if not car_links:
            print("Không có URL nào trong file để xử lý. Dừng lại.")
            return

        playwright, browser, context = await self.setup_browser()
        try:
            await self.extract_data_from_links(context, car_links)
            await self.save_final_data()
            print(f"Hoàn tất! Tổng số xe đã thu thập: {len(self.data)}")
        except Exception as e:
            print(f"Lỗi nghiêm trọng trong quá trình scraping: {e}")
        finally:
            await browser.close()
            await playwright.stop()