from base_scraper import BaseScraper
import os

class NhaTotScraper(BaseScraper):
    async def wait_for_list_elements(self, page, max_retries=3):
        """Chờ và tìm các phần tử bất động sản với nhiều selector khác nhau"""
        print("Đang tìm các phần tử bất động sản...")
        
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
        """Trích xuất dữ liệu từ các danh sách bất động sản"""
        print("Đang trích xuất dữ liệu...")
        
        property_elements = await self.wait_for_list_elements(page)
        print(f"Tìm thấy {len(property_elements)} phần tử bất động sản")
        
        if not property_elements:
            print("Không có phần tử nào để trích xuất, bỏ qua trang này.")
            return
            
        for idx, prop in enumerate(property_elements[:20]):
            try:
                # Trích xuất tiêu đề
                title = "N/A"
                for selector in self.config.TITLE_SELECTORS:
                    title_elem = await prop.query_selector(selector)
                    if title_elem:
                        title = await title_elem.text_content()
                        break
                
                # Trích xuất giá
                price = "N/A"
                for selector in self.config.PRICE_SELECTORS:
                    price_elem = await prop.query_selector(selector)
                    if price_elem:
                        price = await price_elem.text_content()
                        break
                
                # Trích xuất diện tích
                area = "N/A"
                for selector in self.config.AREA_SELECTORS:
                    area_elem = await prop.query_selector(selector)
                    if area_elem:
                        area = await area_elem.text_content()
                        break
                
                # Trích xuất địa điểm
                location = "N/A"
                for selector in self.config.LOCATION_SELECTORS:
                    location_elem = await prop.query_selector(selector)
                    if location_elem:
                        location = await location_elem.text_content()
                        break
                
                # Trích xuất ngày đăng
                date = "N/A"
                for selector in self.config.DATE_SELECTORS:
                    date_elem = await prop.query_selector(selector)
                    if date_elem:
                        date = await date_elem.text_content()
                        break
                
                # Trích xuất thông tin bổ sung
                info = "N/A"
                for selector in self.config.INFO_SELECTORS:
                    info_elem = await prop.query_selector(selector)
                    if info_elem:
                        info = await info_elem.text_content()
                        break
                
                # Lưu dữ liệu
                self.data.append({
                    'title': title.strip(),
                    'price': price.strip(),
                    'area': area.strip(),
                    'location': location.strip(),
                    'info': info.strip(),
                    'date': date.strip(),
                    'page': await page.evaluate('() => window.location.href')
                })
                print(f"Đã trích xuất ({idx+1}/{len(property_elements)}): {title.strip()[:40]}...")
                
            except Exception as e:
                print(f"Lỗi khi trích xuất dữ liệu: {e}")
                continue

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
                        if f"page={current_page + 1}" in current_url:
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
            if f"page={current_page + 1}" in current_url:
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