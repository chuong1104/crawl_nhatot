import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import time
import random

class NhaTotScraper:
    def __init__(self, max_pages=5):
        self.properties_data = []
        self.max_pages = max_pages  # Số trang tối đa cần cào
        
    async def setup_browser(self):
        """Thiết lập trình duyệt với các tùy chọn cần thiết"""
        playwright = await async_playwright().start()
        
        # Tạo trình duyệt với các tùy chọn giả lập user-agent và bypass bảo mật
        browser = await playwright.chromium.launch(
            headless=False,  # Đặt True nếu không muốn thấy trình duyệt
            args=[
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process'
            ]
        )
        
        # Tạo context mới với viewport ngẫu nhiên
        context = await browser.new_context(
            viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            java_script_enabled=True
        )
        
        # Thêm các header để trông giống trình duyệt thật hơn
        await context.add_init_script("""
            delete navigator.__proto__.webdriver;
            window.chrome = {runtime: {}};
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
        """)
        
        return playwright, browser, context

    async def handle_popups(self, page):
        """Xử lý các popup có thể xuất hiện"""
        try:
            # Kiểm tra và xử lý popup cookie/consent nếu có
            cookie_buttons = [
                "button[aria-label='Accept cookies']", 
                "button:has-text('Accept')", 
                "button:has-text('Đồng ý')",
                "button:has-text('Chấp nhận')",
                ".cookie-consent-button",
                "[id*='cookie'] button",
                "[class*='cookie'] button",
                "[id*='consent'] button",
                "[class*='consent'] button"
            ]
            
            for selector in cookie_buttons:
                if await page.query_selector(selector):
                    await page.click(selector)
                    print(f"Đã đóng popup với selector: {selector}")
                    await page.wait_for_timeout(1000)
                    break
                    
        except Exception as e:
            print(f"Lỗi khi xử lý popup: {e}")

    async def auto_scroll(self, page):
        """Tự động scroll trang để load tất cả nội dung"""
        print("Đang scroll để tải thêm dữ liệu...")
        
        # Scroll từ từ để load dữ liệu
        scroll_pause_time = 2.0  # Tăng thời gian chờ sau mỗi lần scroll
        scroll_height = await page.evaluate("document.body.scrollHeight")
        current_scroll_position = 0
        scroll_step = 300  # Giảm khoảng cách scroll để tải dữ liệu tốt hơn
        
        while current_scroll_position < scroll_height:
            # Scroll xuống một đoạn
            current_scroll_position += scroll_step
            await page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
            
            # Chờ một khoảng thời gian ngẫu nhiên
            await page.wait_for_timeout((scroll_pause_time + random.random()) * 1000)
            
            # Kiểm tra chiều cao mới sau khi scroll
            new_scroll_height = await page.evaluate("document.body.scrollHeight")
            if new_scroll_height > scroll_height:
                scroll_height = new_scroll_height
                
            # Dừng lại nếu đã scroll đủ nhiều
            if current_scroll_position > 5000:
                break

    async def wait_for_property_elements(self, page, max_retries=3):
        """Chờ và tìm các phần tử bất động sản với nhiều selector khác nhau"""
        print("Đang tìm các phần tử bất động sản...")
        
        # Cập nhật các selectors dựa trên cấu trúc HTML mới
        selectors = [
            '.c15fd2pn',                        # Wrapper từ mẫu HTML
            'div.c15fd2pn',                     # Thêm div prefix
            'a[itemprop="item"]',               # Anchor từ mẫu HTML
            'a.cqzlgv9',                        # Class của anchor từ mẫu HTML
            '.szp40s8',                         # Container nội dung từ mẫu HTML
            'div.szp40s8',                      # Thêm div prefix
            'div:has(> h3[class*="a3f35hz"])',  # Div chứa tiêu đề từ mẫu HTML
            '.szp40s8.r9vw5if',                 # Kết hợp các class từ mẫu HTML
            'div.AdItem_wrapperAdItem__S6qPH',  # Selector cũ nhưng vẫn thử
            '.AdsList_adsListContainers__JW7pj > div', # Wrapper chung cho danh sách
            '.adsListBottom > div'              # Wrapper khác cho danh sách
        ]
        
        for retry in range(max_retries):
            for selector in selectors:
                try:
                    print(f"Thử selector: {selector}, lần thử: {retry+1}")
                    elements = await page.query_selector_all(selector)
                    
                    if elements and len(elements) > 0:
                        print(f"Đã tìm thấy {len(elements)} phần tử với selector: {selector}")
                        return elements
                        
                    # Nếu không tìm thấy phần tử ngay lập tức, thử đợi
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
            
            # Nếu tất cả các selector đều thất bại, scroll thêm và thử lại
            print(f"Không tìm thấy phần tử, đang scroll thêm và thử lại...")
            await page.evaluate("window.scrollBy(0, 700)")
            await page.wait_for_timeout(5000)
        
        # Nếu không tìm thấy phần tử sau tất cả các lần thử, chụp ảnh màn hình
        print("Đang chụp ảnh màn hình để kiểm tra...")
        await page.screenshot(path="debug_screenshot.png")
        print("Đã lưu ảnh màn hình vào debug_screenshot.png")
        
        # Thử lấy HTML của trang để debug
        html = await page.content()
        with open("page_content.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Đã lưu nội dung HTML vào page_content.html để debug")
        
        # Thử trả về các phần tử bất kỳ có chứa thông tin bất động sản
        fallback_selectors = [
            'div:has(h3):has(span[style*="color: rgb(240, 50, 94)"])', # Div có h3 và span giá
            'div:has(h3):has(span[style*="color: rgb(34, 34, 34)"])',  # Div có h3 và span diện tích
            'div:has(.sqqmhlc)',                                       # Div có container giá và diện tích
            'div:has(svg#LocationFilled)'                              # Div có biểu tượng địa điểm
        ]
        
        for selector in fallback_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements and len(elements) > 0:
                    print(f"Đã tìm thấy {len(elements)} phần tử với selector dự phòng: {selector}")
                    return elements
            except Exception:
                pass
                
        # Nếu tất cả đều thất bại, trả về danh sách rỗng để script không bị dừng
        print("Không tìm thấy phần tử nào, tiếp tục với trang tiếp theo.")
        return []

    async def extract_property_data(self, page):
        """Trích xuất dữ liệu từ các danh sách bất động sản"""
        print("Đang trích xuất dữ liệu...")
        
        # Lấy tất cả các thẻ chứa thông tin bất động sản
        property_elements = await self.wait_for_property_elements(page)
        print(f"Tìm thấy {len(property_elements)} phần tử bất động sản")
        
        if not property_elements:
            print("Không có phần tử nào để trích xuất, bỏ qua trang này.")
            return
            
        for idx, prop in enumerate(property_elements[:20]):  # Giới hạn số lượng để tránh bị chặn
            try:
                # Trích xuất tiêu đề - cập nhật theo mẫu HTML
                title = "N/A"
                for title_selector in ['h3.a3f35hz', 'h3[class*="a1ygob26"]', 'h3', '.szp40s8 h3']:
                    title_elem = await prop.query_selector(title_selector)
                    if title_elem:
                        title = await title_elem.text_content()
                        break
                
                # Trích xuất giá - cập nhật theo mẫu HTML
                price = "N/A"
                for price_selector in ['span.bfe6oav[style*="color: rgb(240, 50, 94)"]', 'span[class*="t1dp97gi"]', '.sqqmhlc span:first-child']:
                    price_elem = await prop.query_selector(price_selector)
                    if price_elem:
                        price = await price_elem.text_content()
                        break
                
                # Trích xuất diện tích - cập nhật theo mẫu HTML
                area = "N/A"
                for area_selector in ['span.bfe6oav[style*="color: rgb(34, 34, 34)"]', 'span[class*="t1e1b6m2"]', '.sqqmhlc span:last-child']:
                    area_elem = await prop.query_selector(area_selector)
                    if area_elem:
                        area = await area_elem.text_content()
                        break
                
                # Trích xuất địa điểm - cập nhật theo mẫu HTML
                location = "N/A"
                for loc_selector in ['span.c1u6gyxh[style*="color: rgb(140, 140, 140)"]', 'span[class*="t1u18gyr"]', 'div:has(> svg#LocationFilled) + span']:
                    location_elem = await prop.query_selector(loc_selector)
                    if location_elem:
                        location = await location_elem.text_content()
                        break
                
                # Trích xuất ngày đăng - cập nhật theo mẫu HTML
                date = "N/A"
                for date_selector in ['span.c1u6gyxh[style*="color: rgb(255, 255, 255)"]', 'span[class*="tx5yyjc"]', '.m1vb9shx span']:
                    date_elem = await prop.query_selector(date_selector)
                    if date_elem:
                        date = await date_elem.text_content()
                        break
                
                # Trích xuất thông tin bổ sung - phòng ngủ, hướng nhà
                info = "N/A"
                for info_selector in ['span.bwq0cbs', 'span[class*="tle2ik0"]', '.szp40s8 > span']:
                    info_elem = await prop.query_selector(info_selector)
                    if info_elem:
                        info = await info_elem.text_content()
                        break
                
                # Lưu dữ liệu
                self.properties_data.append({
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
            
            # Scroll đến cuối trang để hiển thị nút phân trang
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(2000)
            
            # Chụp ảnh màn hình trước khi chuyển trang (để debug)
            await page.screenshot(path=f"pagination_before_page{current_page}.png")
            
            # Cách 1: Sử dụng phân trang
            pagination_selectors = [
                f'a[href*="page={current_page + 1}"]',
                f'.Paging_pagingItem__Y3r2u a[href*="page={current_page + 1}"]',
                'button.Paging_redirectPageBtn__KvsqJ:has(i.Paging_rightIcon__3p8MS)',
                'i.Paging_rightIcon__3p8MS',
                'button:has(i[class*="rightIcon"])'
            ]
            
            for selector in pagination_selectors:
                try:
                    print(f"Tìm kiếm nút phân trang với selector: {selector}")
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Đã tìm thấy nút phân trang với selector: {selector}")
                        
                        # Đảm bảo element hiển thị trong viewport
                        await element.scroll_into_view_if_needed()
                        await page.wait_for_timeout(1000)
                        
                        # Click và đợi trang tải
                        await element.click()
                        print(f"Đã nhấn nút sang trang {current_page + 1}")
                        await page.wait_for_load_state('domcontentloaded')
                        await page.wait_for_timeout(5000)
                        
                        # Kiểm tra xem đã chuyển trang thành công chưa
                        current_url = await page.evaluate('() => window.location.href')
                        if f"page={current_page + 1}" in current_url:
                            print(f"Đã chuyển trang thành công: {current_url}")
                            return True
                except Exception as e:
                    print(f"Không thể click vào {selector}: {e}")
            
            # Cách 2: Điều hướng trực tiếp đến URL trang tiếp theo
            url = f"https://www.nhatot.com/thue-bat-dong-san-ha-noi?page={current_page + 1}"
            print(f"Thử điều hướng trực tiếp đến URL: {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_load_state('networkidle')
            await page.wait_for_timeout(5000)
            
            # Kiểm tra URL sau khi điều hướng
            current_url = await page.evaluate('() => window.location.href')
            if f"page={current_page + 1}" in current_url:
                print(f"Đã chuyển trực tiếp đến URL trang {current_page + 1} thành công")
                return True
            else:
                print(f"Chuyển trang không thành công. URL hiện tại: {current_url}")
                return False
                
        except Exception as e:
            print(f"Lỗi khi chuyển trang: {e}")
            await page.screenshot(path=f"pagination_error_page{current_page}.png")
            return False

    async def scrape(self):
        """Hàm chính để thực hiện scraping"""
        print("Bắt đầu scraping dữ liệu từ Nhà Tốt...")
        
        playwright, browser, context = await self.setup_browser()
        
        try:
            # Tạo trang mới
            page = await context.new_page()
            
            # Điều hướng đến URL
            await page.goto('https://www.nhatot.com/thue-bat-dong-san-ha-noi', timeout=90000)
            print("Đã tải trang web thành công")
            
            # Chờ dài hơn để trang web load hoàn toàn
            await page.wait_for_timeout(8000)
            
            # Xử lý các popup nếu có
            await self.handle_popups(page)
            
            # Thêm vòng lặp để cào nhiều trang
            current_page = 1
            
            while current_page <= self.max_pages:
                print(f"\n--- ĐANG XỬ LÝ TRANG {current_page} ---\n")
                
                try:
                    # Thực hiện auto-scroll
                    await self.auto_scroll(page)
                    
                    # Trích xuất dữ liệu
                    await self.extract_property_data(page)
                    
                    # Lưu dữ liệu đã cào được sau mỗi trang
                    if self.properties_data:
                        print(f"Lưu dữ liệu tạm thời sau khi xử lý trang {current_page}...")
                        temp_df = pd.DataFrame(self.properties_data)
                        temp_df.to_csv(f'nhatot_properties_partial.csv', index=False, encoding='utf-8-sig')
                        print(f"Đã lưu {len(self.properties_data)} bản ghi vào file tạm.")
                    
                    # Nếu đã đến trang cuối, dừng lại
                    if current_page == self.max_pages:
                        break
                        
                    # Chuyển sang trang tiếp theo
                    success = await self.go_to_next_page(page, current_page)
                    if not success:
                        print(f"Không thể chuyển sang trang {current_page + 1}, dừng việc cào dữ liệu.")
                        break
                        
                    # Tăng số trang hiện tại
                    current_page += 1
                    
                    # Nghỉ ngẫu nhiên giữa các trang để tránh bị phát hiện
                    pause_time = 3 + random.random() * 3
                    print(f"Đợi {pause_time:.2f} giây trước khi xử lý trang tiếp theo...")
                    await page.wait_for_timeout(pause_time * 1000)
                    
                except Exception as e:
                    print(f"Lỗi khi xử lý trang {current_page}: {e}")
                    await page.screenshot(path=f"error_page_{current_page}.png")
                    
                    # Thử lưu dữ liệu đã cào được
                    if self.properties_data:
                        print("Lưu dữ liệu đã cào được trước khi tiếp tục...")
                        temp_df = pd.DataFrame(self.properties_data)
                        temp_df.to_csv(f'nhatot_properties_temp_{current_page}.csv', index=False, encoding='utf-8-sig')
                    
                    # Nếu là lỗi mạng hoặc trang web, thử làm mới trang
                    try:
                        await page.reload()
                        await page.wait_for_load_state('networkidle')
                        await page.wait_for_timeout(5000)
                    except:
                        break
            
            # Lưu dữ liệu ra file CSV
            if self.properties_data:
                df = pd.DataFrame(self.properties_data)
                df.to_csv('nhatot_properties.csv', index=False, encoding='utf-8-sig')
                print(f"Đã lưu {len(self.properties_data)} bản ghi vào file nhatot_properties.csv")
                
                # Hiển thị dữ liệu mẫu
                print("\n5 bản ghi đầu tiên:")
                print(df.head().to_string(index=False))
            else:
                print("Không tìm thấy dữ liệu nào")
                
        except Exception as e:
            print(f"Lỗi trong quá trình scraping: {e}")
            # Chụp ảnh màn hình để debug
            try:
                await page.screenshot(path="error_screenshot.png")
                print("Đã lưu ảnh màn hình lỗi vào error_screenshot.png")
            except:
                pass
        finally:
            # Đóng trình duyệt
            await browser.close()
            await playwright.stop()

# Chạy scraper
async def main():
    scraper = NhaTotScraper(max_pages=20)
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())