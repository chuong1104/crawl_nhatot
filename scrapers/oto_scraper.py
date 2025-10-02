import asyncio
import re
import pandas as pd
from base_scraper import BaseScraper
from utils import normalize_car_data, extract_price, extract_km, extract_year, clean_text, clean_car_name

class OtoComVnScraper(BaseScraper):
    def __init__(self, config, max_pages):
        super().__init__(config, max_pages)
        self.input_file = "final_aidxc_urls.csv" # File chứa URL đầu vào
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
        """Trích xuất thông tin chi tiết của xe từ trang chi tiết."""
        car_info = {}
        current_url = page.url
        car_info['ad_id'] = self.extract_ad_id_from_url(current_url) or 'N/A'

        # Lấy tiêu đề
        title_elem = await page.query_selector(self.config.TITLE_SELECTORS[0])
        car_info['title'] = clean_text(await title_elem.text_content()) if title_elem else 'N/A'

        # Lấy giá
        price_elem = await page.query_selector(self.config.PRICE_SELECTORS[0])
        car_info['price'] = extract_price(await price_elem.text_content()) if price_elem else None

        # Lấy ngày đăng
        date_elem = await page.query_selector(self.config.DATE_POSTED_SELECTORS[0])
        car_info['date_posted'] = clean_text(await date_elem.text_content()) if date_elem else 'N/A'

        # Lấy các thông tin chi tiết khác
        for key, selector in self.config.DETAIL_SELECTORS.items():
            elem = await page.query_selector(selector)
            if elem:
                text = await elem.text_content()
                value = text.split(':')[-1].strip() if ':' in text else text.strip()
                car_info[key] = clean_text(value) if value else 'N/A'
            else:
                car_info[key] = 'N/A'

        return self.normalize_car_data_simple(car_info)

    def normalize_car_data_simple(self, car_data):
        """Chuẩn hóa dữ liệu thô thành định dạng sạch."""
        normalized = car_data.copy()
        
        if 'title' in normalized:
            normalized['title'] = clean_car_name(normalized['title'])
        
        if 'price' in normalized and normalized['price'] is not None:
            try:
                normalized['price'] = int(normalized['price'])
            except (ValueError, TypeError):
                normalized['price'] = None
        
        if 'km_driven' in normalized and normalized['km_driven'] != 'N/A':
            normalized['km_driven'] = extract_km(normalized['km_driven'])
        
        if 'manufacture_year' in normalized and normalized['manufacture_year'] != 'N/A':
            normalized['manufacture_year'] = extract_year(normalized['manufacture_year'])
        
        return normalized

    async def scrape(self):
        """Ghi đè phương thức scrape để đọc URL từ file CSV và cào dữ liệu song song."""
        print(f"Bắt đầu scraping dữ liệu từ file {self.input_file}...")
        try:
            df = pd.read_csv(self.input_file)
            car_links = df['final_url'].dropna().unique().tolist()
            print(f"Tìm thấy {len(car_links)} URL duy nhất để cào.")
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file {self.input_file}. Hãy chạy 'python collect_urls.py' trước.")
            return
        except Exception as e:
            print(f"Lỗi khi đọc file CSV: {e}")
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