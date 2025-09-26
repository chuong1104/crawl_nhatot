from base_scraper import BaseScraper
import os
import asyncio
from utils import normalize_car_data, extract_price, extract_km, extract_year, clean_text
class OtoComVnScraper(BaseScraper):
    async def handle_load_more(self, page, max_clicks=10):
        """Xử lý nút 'Hiển thị thêm' trên trang danh sách"""
        click_count = 0
        while click_count < max_clicks:
            try:
                # Scroll xuống cuối trang để tìm nút
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(3000)
                
                # Kiểm tra xem nút có tồn tại không
                load_more_button = await page.query_selector(self.config.LOAD_MORE_SELECTOR)
                
                if load_more_button:
                    # Kiểm tra xem nút có thể click được không
                    is_visible = await load_more_button.is_visible()
                    is_enabled = await load_more_button.is_enabled()
                    
                    if is_visible and is_enabled:
                        await load_more_button.scroll_into_view_if_needed()
                        await page.wait_for_timeout(1000)
                        
                        # Click vào nút
                        await load_more_button.click()
                        click_count += 1
                        print(f"Đã click vào nút 'Hiển thị thêm' lần thứ {click_count}")
                        
                        # Chờ dữ liệu mới tải về
                        await page.wait_for_timeout(5000)
                        
                        # Scroll thêm để kích hoạt các phần tử mới
                        await page.evaluate("window.scrollBy(0, 300)")
                        await page.wait_for_timeout(2000)
                    else:
                        print("Nút 'Hiển thị thêm' không thể click được")
                        break
                else:
                    print("Không tìm thấy nút 'Hiển thị thêm' nữa")
                    break
                    
            except Exception as e:
                print(f"Lỗi khi xử lý nút 'Hiển thị thêm': {e}")
                break

    async def wait_for_list_elements(self, page, max_retries=3):
        """Chờ và tìm các phần tử xe với nhiều selector khác nhau"""
        print("Đang tìm các phần tử xe...")
        
        # Xử lý nút "Hiển thị thêm" trước khi lấy danh sách
        await self.handle_load_more(page)
        
        for retry in range(max_retries):
            for selector in self.config.PROPERTY_SELECTORS:
                try:
                    print(f"Thử selector: {selector}, lần thử: {retry+1}")
                    elements = await page.query_selector_all(selector)
                    
                    if elements and len(elements) > 0:
                        print(f"Đã tìm thấy {len(elements)} phần tử với selector: {selector}")
                        return elements
                        
                    try:
                        await page.wait_for_selector(selector, timeout=10000, state="visible")
                        elements = await page.query_selector_all(selector)
                        if elements and len(elements) > 0:
                            print(f"Đã tìm thấy {len(elements)} phần tử sau khi đợi với selector: {selector}")
                            return elements
                    except Exception:
                        pass
                        
                except Exception as e:
                    print(f"Không tìm thấy phần tử với selector: {selector}, lỗi: {str(e)[:100]}...")
            
            print(f"Không tìm thấy phần tử, đang scroll thêm và thử lại...")
            await page.evaluate("window.scrollBy(0, 700)")
            await page.wait_for_timeout(5000)
        
        await self.save_debug_info(page, "debug")
        
        # Thử với selectors dự phòng
        for selector in self.config.FALLBACK_SELECTORS:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"Đã tìm thấy {len(elements)} phần tử với selector dự phòng: {selector}")
                    return elements
            except Exception:
                pass
                
        print("Không tìm thấy phần tử nào, tiếp tục với trang tiếp theo.")
        return []

    async def extract_data(self, page):
        """Trích xuất dữ liệu từ các danh sách xe"""
        print("Đang trích xuất dữ liệu...")
        
        property_elements = await self.wait_for_list_elements(page)
        print(f"Tìm thấy {len(property_elements)} phần tử xe")
        
        if not property_elements:
            print("Không có phần tử nào để trích xuất, bỏ qua trang này.")
            return
            
        # Lấy danh sách các link xe
        car_links = []
        for idx, prop in enumerate(property_elements):
            try:
                href = await prop.get_attribute('href')
                if href:
                    full_url = href if href.startswith('http') else f"https://oto.com.vn{href}"
                    car_links.append(full_url)
                    print(f"Đã tìm thấy link xe {idx+1}: {full_url}")
            except Exception as e:
                print(f"Lỗi khi trích xuất link: {e}")
                continue
        
        # Với mỗi link xe, truy cập và trích xuất thông tin chi tiết
        for idx, car_url in enumerate(car_links):
            try:
                print(f"Đang xử lý xe {idx+1}/{len(car_links)}: {car_url}")
                # Mở tab mới
                context = page.context
                new_page = await context.new_page()
                await new_page.goto(car_url, timeout=60000)
                await new_page.wait_for_load_state('networkidle')
                await asyncio.sleep(2)  # Chờ ổn định

                # Trích xuất thông tin chi tiết
                car_info = await self.extract_car_detail(new_page)
                car_info['url'] = car_url
                self.data.append(car_info)
                print(f"Đã trích xuất thông tin xe {idx+1}: {car_info.get('title', 'N/A')}")

                # Đóng tab
                await new_page.close()
                
                # Nghỉ giữa các request để tránh bị chặn
                await asyncio.sleep(2)

            except Exception as e:
                print(f"Lỗi khi xử lý xe {car_url}: {e}")
                await self.save_error_info(page, e, f"car_{idx}")
                if 'new_page' in locals():
                    await new_page.close()

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
            except Exception as e:
                continue
        
        if 'title' not in car_info:
            car_info['title'] = 'N/A'

        # Lấy giá xe với nhiều selector khác nhau
        price_raw = 'N/A'
        for selector in self.config.PRICE_SELECTORS:
            try:
                price_elems = await page.query_selector_all(selector)
                for price_elem in price_elems:
                    price_text = await price_elem.text_content()
                    if price_text and any(char.isdigit() for char in price_text):
                        price_raw = clean_text(price_text)
                        break
                if price_raw != 'N/A':
                    break
            except Exception as e:
                continue
        
        # Sử dụng hàm extract_price từ utils
        price_value = extract_price(price_raw)
        car_info['price_raw'] = price_raw
        car_info['price_value'] = price_value
        car_info['price_display'] = f"{price_value:,.0f} VND" if price_value else 'N/A'
               
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
            except Exception as e:
                continue

        # Lấy các thông tin từ box-info-detail
        for key, selector in self.config.DETAIL_SELECTORS.items():
            try:
                elem = await page.query_selector(selector)
                if elem:
                    # Lấy nội dung, bỏ nhãn
                    text = await elem.text_content()
                    # Xóa nhãn (có thể dùng split hoặc replace)
                    value = text.split(':')[-1].strip() if ':' in text else text.strip()
                    car_info[key] = value
                else:
                    car_info[key] = 'N/A'
            except Exception as e:
                print(f"Lỗi khi lấy {key}: {e}")
                car_info[key] = 'N/A'

        # Xử lý đặc biệt cho km_driven để đảm bảo lấy đúng số km
        if 'km_driven' in car_info and car_info['km_driven'] != 'N/A':
            km_text = car_info['km_driven']
            # Nếu có dạng "3.900 km" nhưng bị hiểu là 3.9, cần xử lý riêng
            if '.' in str(km_text):
                parts = str(km_text).split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # Đây là dạng 3.900 -> thực tế là 3900 km
                    actual_km = int(parts[0]) * 1000 + int(parts[1])
                    car_info['km_driven'] = f"{actual_km} km"

        # Chuẩn hóa dữ liệu sử dụng hàm normalize_car_data
        normalized_info = normalize_car_data(car_info)
        return normalized_info

    def clean_price_text(self, price_text):
        """Làm sạch text giá xe, chỉ giữ lại phần chứa số"""
        if not price_text:
            return None
        
        # Loại bỏ các từ không cần thiết
        unwanted_phrases = ['Giá xe ô tô', 'Giá', 'Giá xe', 'Giá bán']
        cleaned_text = price_text.strip()
        
        for phrase in unwanted_phrases:
            cleaned_text = cleaned_text.replace(phrase, '').strip()
        
        # Tìm phần chứa số (triệu, tỷ, etc.)
        import re
        # Tìm pattern chứa số và đơn vị tiền tệ
        price_pattern = r'(\d+[.,]?\d*[\s]*(triệu|tỷ|tỉ|tr|nghìn|k|đồng)?)'
        matches = re.findall(price_pattern, cleaned_text, re.IGNORECASE)
        
        if matches:
            # Lấy match đầu tiên
            price_match = matches[0][0]
            return price_match.strip()
        
        # Nếu không tìm thấy pattern, trả về text gốc đã làm sạch
        return cleaned_text if any(char.isdigit() for char in cleaned_text) else None

    async def go_to_next_page(self, page, current_page):
        """Di chuyển đến trang tiếp theo"""
        try:
            print(f"Đang chuyển sang trang {current_page + 1}...")
            
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Chụp ảnh màn hình trước khi chuyển trang (để debug)
            screenshot_path = os.path.join(self.config.SCREENSHOTS_DIR, f"pagination_before_page{current_page}.png")
            await page.screenshot(path=screenshot_path)
            
            # Thử các selectors của nút phân trang
            for selector_template in self.config.PAGINATION_SELECTORS:
                try:
                    selector = selector_template.format(current_page + 1) if "{}" in selector_template else selector_template
                    print(f"Tìm kiếm nút phân trang với selector: {selector}")
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Đã tìm thấy nút phân trang với selector: {selector}")
                        
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(1000)
                        
                        await element.click()
                        print(f"Đã nhấn nút sang trang {current_page + 1}")
                        await page.wait_for_load_state('domcontentloaded')
                        await page.wait_for_timeout(5000)
                        
                        current_url = await page.evaluate('() => window.location.href')
                        if f"/p{current_page + 1}" in current_url or f"page={current_page + 1}" in current_url:
                            print(f"Đã chuyển trang thành công: {current_url}")
                            return True
                except Exception as e:
                    print(f"Không thể click vào {selector}: {e}")
            
            # Thử điều hướng trực tiếp
            url = self.config.PAGINATION_URL_TEMPLATE.format(current_page + 1)
            print(f"Thử điều hướng trực tiếp đến URL: {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(5000)
            
            current_url = await page.evaluate('() => window.location.href')
            if f"/p{current_page + 1}" in current_url or f"page={current_page + 1}" in current_url:
                print(f"Đã chuyển trực tiếp đến URL trang {current_page + 1} thành công")
                return True
            else:
                print(f"Chuyển trang không thành công. URL hiện tại: {current_url}")
                return False
                
        except Exception as e:
            print(f"Lỗi khi chuyển trang: {e}")
            error_screenshot_path = os.path.join(self.config.ERRORS_DIR, f"pagination_error_page{current_page}.png")
            await page.screenshot(path=error_screenshot_path)
            return False