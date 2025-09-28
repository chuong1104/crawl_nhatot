from base_scraper import BaseScraper
import os
import asyncio
from utils import normalize_car_data, extract_price, extract_km, extract_year, clean_text, clean_car_name  
class OtoComVnScraper(BaseScraper):
    def __init__(self, config, max_pages):
        super().__init__(config, max_pages)
        self.seen_urls = set()  # Để theo dõi URL đã xử lý, tránh trùng lặp
        self.load_more_count = 0  # Đếm số lần đã nhấn "Hiển thị thêm"

    async def handle_load_more(self, page, max_clicks=None):
        """Xử lý nút 'Hiển thị thêm' với số lần click có thể tùy chỉnh"""
        if max_clicks is None:
            max_clicks = self.max_pages  # Sử dụng max_pages làm số lần click tối đa
        
        click_count = 0
        while click_count < max_clicks:
            try:
                # Scroll xuống cuối trang để tìm nút
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                
                # Kiểm tra xem nút có tồn tại và hiển thị không
                load_more_button = await page.query_selector(self.config.LOAD_MORE_SELECTOR)
                
                if load_more_button:
                    is_visible = await load_more_button.is_visible()
                    is_enabled = await load_more_button.is_enabled()
                    
                    if is_visible and is_enabled:
                        await load_more_button.scroll_into_view_if_needed()
                        await page.wait_for_timeout(1000)
                        
                        # Click vào nút
                        await load_more_button.click()
                        click_count += 1
                        self.load_more_count += 1
                        print(f"Đã click vào nút 'Hiển thị thêm' lần thứ {self.load_more_count}")
                        
                        # Chờ dữ liệu mới tải về
                        await page.wait_for_timeout(5000)
                        
                        # Scroll thêm để kích hoạt lazy loading nếu có
                        await page.evaluate("window.scrollBy(0, 500)")
                        await page.wait_for_timeout(2000)
                    else:
                        print("Nút 'Hiển thị thêm' không thể click được, dừng lại")
                        break
                else:
                    print("Không tìm thấy nút 'Hiển thị thêm' nữa, có thể đã hết dữ liệu")
                    break
                    
            except Exception as e:
                print(f"Lỗi khi xử lý nút 'Hiển thị thêm': {e}")
                break
        
        return click_count

    async def wait_for_list_elements(self, page, max_retries=3):
        """Chờ và tìm các phần tử xe"""
        print("Đang tìm các phần tử xe...")
        
        # Xử lý nút "Hiển thị thêm" trước khi lấy danh sách
        clicks_done = await self.handle_load_more(page)
        print(f"Đã thực hiện {clicks_done} lần nhấn 'Hiển thị thêm'")
        
        for retry in range(max_retries):
            for selector in self.config.PROPERTY_SELECTORS:
                try:
                    print(f"Thử selector: {selector}, lần thử: {retry+1}")
                    elements = await page.query_selector_all(selector)
                    
                    if elements and len(elements) > 0:
                        print(f"Đã tìm thấy {len(elements)} phần tử với selector: {selector}")
                        return elements
                        
                    # Thử đợi selector xuất hiện
                    try:
                        await page.wait_for_selector(selector, timeout=10000, state="attached")
                        elements = await page.query_selector_all(selector)
                        if elements and len(elements) > 0:
                            print(f"Đã tìm thấy {len(elements)} phần tử sau khi đợi với selector: {selector}")
                            return elements
                    except Exception:
                        pass
                        
                except Exception as e:
                    print(f"Không tìm thấy phần tử với selector: {selector}, lỗi: {str(e)[:100]}...")
            
            if retry < max_retries - 1:
                print(f"Không tìm thấy phần tử, đang scroll thêm và thử lại... (lần {retry+1})")
                await page.evaluate("window.scrollBy(0, 800)")
                await page.wait_for_timeout(5000)
        
        # Thử với selectors dự phòng
        for selector in self.config.FALLBACK_SELECTORS:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"Đã tìm thấy {len(elements)} phần tử với selector dự phòng: {selector}")
                    return elements
            except Exception:
                pass
                
        print("Không tìm thấy phần tử nào")
        return []

    async def extract_data(self, page):
        """Trích xuất dữ liệu từ các danh sách xe, tránh trùng lặp"""
        print("Đang trích xuất dữ liệu...")
        
        property_elements = await self.wait_for_list_elements(page)
        print(f"Tìm thấy {len(property_elements)} phần tử xe")
        
        if not property_elements:
            print("Không có phần tử nào để trích xuất")
            return
            
        # Lấy danh sách các link xe và loại bỏ trùng lặp
        car_links = []
        for idx, prop in enumerate(property_elements):
            try:
                href = await prop.get_attribute('href')
                if href:
                    full_url = href if href.startswith('http') else f"https://oto.com.vn{href}"
                    
                    # FILTER: Chỉ lấy các link chứa '/mua-ban-xe-' (link xe thật)
                    if '/mua-ban-xe-' in full_url:
                        # Kiểm tra trùng lặp
                        if full_url not in self.seen_urls:
                            car_links.append(full_url)
                            self.seen_urls.add(full_url)
                            print(f"Đã tìm thấy link xe {len(car_links)}: {full_url}")
                    else:
                        print(f"Bỏ qua link không phải xe: {full_url}")
            except Exception as e:
                print(f"Lỗi khi trích xuất link: {e}")
                continue
        
        print(f"Tổng số xe không trùng lặp: {len(car_links)}")
        
        # Với mỗi link xe, truy cập và trích xuất thông tin chi tiết
        for idx, car_url in enumerate(car_links):
            try:
                print(f"Đang xử lý xe {idx+1}/{len(car_links)}: {car_url}")
                
                # Mở tab mới
                context = page.context
                new_page = await context.new_page()
                
                # Đặt timeout và retry cho việc tải trang
                max_retries = 2
                for retry in range(max_retries):
                    try:
                        await new_page.goto(car_url, timeout=60000, wait_until='networkidle')
                        break
                    except Exception as e:
                        if retry == max_retries - 1:
                            raise e
                        print(f"Lỗi khi tải trang, thử lại lần {retry+1}: {e}")
                        await asyncio.sleep(3)
                
                await asyncio.sleep(2)  # Chờ ổn định

                # Trích xuất thông tin chi tiết
                car_info = await self.extract_car_detail(new_page)
                car_info['url'] = car_url
                self.data.append(car_info)
                print(f"Đã trích xuất thông tin xe {idx+1}: {car_info.get('title', 'N/A')}")

                # Đóng tab
                await new_page.close()
                
                # Nghỉ giữa các request để tránh bị chặn
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Lỗi khi xử lý xe {car_url}: {e}")
                await self.save_error_info(page, e, f"car_{idx}")
                if 'new_page' in locals():
                    try:
                        await new_page.close()
                    except:
                        pass  # Ignore errors when closing page

    async def extract_car_detail(self, page):
        """Trích xuất thông tin chi tiết của xe từ trang chi tiết"""
        car_info = {}

        # Lấy tiêu đề
        for selector in self.config.TITLE_SELECTORS:
            try:
                title_elem = await page.query_selector(selector)
                if title_elem:
                    title_text = await title_elem.text_content()
                    if title_text and title_text.strip():
                        car_info['title'] = clean_text(title_text)
                        break
            except Exception:
                continue
        
        if 'title' not in car_info:
            car_info['title'] = 'N/A'

        # Lấy giá xe - chỉ lấy giá trị số
        car_info['price'] = None
        
        for selector in self.config.PRICE_SELECTORS:
            try:
                price_elems = await page.query_selector_all(selector)
                for price_elem in price_elems:
                    price_text = await price_elem.text_content()
                    if price_text and any(char.isdigit() for char in price_text):
                        price_value = extract_price(price_text)
                        if price_value is not None:
                            car_info['price'] = price_value
                            break
                if car_info['price'] is not None:
                    break
            except Exception:
                continue

        # Lấy ngày đăng bài
        car_info['date_posted'] = 'N/A'
        for selector in self.config.DATE_POSTED_SELECTORS:
            try:
                date_elem = await page.query_selector(selector)
                if date_elem:
                    date_text = await date_elem.text_content()
                    if date_text and date_text.strip():
                        car_info['date_posted'] = clean_text(date_text)
                        break
            except Exception:
                continue

        # Xử lý nút "Hiển thị thêm" cho mô tả
        # try:
        #     show_more_button = await page.query_selector(self.config.SHOW_MORE_DESCRIPTION_SELECTOR)
        #     if show_more_button:
        #         is_visible = await show_more_button.is_visible()
        #         if is_visible:
        #             await show_more_button.scroll_into_view_if_needed()
        #             await page.wait_for_timeout(1000)
        #             await show_more_button.click()
        #             print("Đã click nút 'Hiển thị thêm' để mở rộng mô tả")
        #             await page.wait_for_timeout(2000)
        # except Exception as e:
        #     print(f"Lỗi khi click nút 'Hiển thị thêm' trong trang chi tiết: {e}")

        # Lấy các thông tin từ box-info-detail
        for key, selector in self.config.DETAIL_SELECTORS.items():
            try:
                elem = await page.query_selector(selector)
                if elem:
                    text = await elem.text_content()
                    value = text.split(':')[-1].strip() if ':' in text else text.strip()
                    car_info[key] = clean_text(value)
                else:
                    car_info[key] = 'N/A'
            except Exception:
                car_info[key] = 'N/A'

        # Lấy mô tả (sau khi đã mở rộng)
        try:
            desc_elem = await page.query_selector(self.config.DESCRIPTION_SELECTOR)
            if desc_elem:
                description_raw = await desc_elem.text_content()
                car_info['description'] = clean_text(description_raw)
            else:
                car_info['description'] = 'N/A'
        except Exception:
            car_info['description'] = 'N/A'

        # Chuẩn hóa dữ liệu
        normalized_info = self.normalize_car_data_simple(car_info)
        return normalized_info

    def normalize_car_data_simple(self, car_data):
        """Chuẩn hóa đơn giản - chỉ giữ lại giá trị số cho price"""
        normalized = car_data.copy()
        
        if 'title' in normalized:
            from utils import clean_car_name
            normalized['title'] = clean_car_name(normalized['title'])
        
        # Đảm bảo price là số nguyên
        if 'price' in normalized and normalized['price'] is not None:
            normalized['price'] = int(normalized['price'])
        
        if 'km_driven' in normalized and normalized['km_driven'] != 'N/A':
            km_value = extract_km(normalized['km_driven'])
            if km_value:
                normalized['km_driven'] = int(km_value)
        
        if 'manufacture_year' in normalized and normalized['manufacture_year'] != 'N/A':
            year_value = extract_year(normalized['manufacture_year'])
            if year_value:
                # Ensure we get the full year, not just "20"
                if 1900 <= year_value <= 2030:
                    normalized['manufacture_year'] = year_value
        
        # Chuẩn hóa các trường text khác
        text_fields = ['fuel', 'transmission', 'condition', 'origin', 'location']
        for field in text_fields:
            if field in normalized and normalized[field] != 'N/A':
                normalized[field] = clean_text(normalized[field])
        
        if 'description' in normalized and normalized['description'] != 'N/A':
            normalized['description'] = clean_text(normalized['description'])
        
        return normalized

    async def go_to_next_page(self, page, current_page):
        """Với cơ chế scroll + load more, không cần chuyển trang theo cách cũ"""
        # Thay vì chuyển trang, chúng ta sẽ xử lý load more trong wait_for_list_elements
        # Phương thức này giữ nguyên để tương thích với base class
        return False  # Trả về False để dừng vòng lặp phân trang truyền thống

    async def scrape(self):
        """Ghi đè phương thức scrape để phù hợp với cơ chế load more"""
        print(f"Bắt đầu scraping dữ liệu từ {self.config.SITE_NAME}...")
        print(f"Số lần nhấn 'Hiển thị thêm' tối đa: {self.max_pages}")
        
        playwright, browser, context = await self.setup_browser()
        
        try:
            page = await context.new_page()
            await page.goto(self.config.START_URL, timeout=self.config.PAGE_LOAD_TIMEOUT)
            print("Đã tải trang web thành công")
            
            await page.wait_for_timeout(self.config.INITIAL_WAIT_TIME)
            await self.handle_popups(page)
            
            # Chỉ cần gọi extract_data một lần, vì nó sẽ tự động xử lý load more
            await self.extract_data(page)
                
            await self.save_final_data()
            print(f"Tổng số xe đã thu thập: {len(self.data)}")
            print(f"Tổng số lần nhấn 'Hiển thị thêm': {self.load_more_count}")
                
        except Exception as e:
            print(f"Lỗi trong quá trình scraping: {e}")
            await self.save_debug_info(page, "error")
        finally:
            await browser.close()
            await playwright.stop()