import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import time
import random
import os

class BaseScraper:
    def __init__(self, config, max_pages):
        self.config = config
        self.data = []
        self.max_pages = max_pages
        
    async def setup_browser(self):
        """Thiết lập trình duyệt với các tùy chọn cần thiết"""
        playwright = await async_playwright().start()
        
        browser = await playwright.chromium.launch(
            headless=self.config.HEADLESS,
            args=self.config.BROWSER_ARGS
        )
        
        context = await browser.new_context(
            viewport={'width': random.randint(1200, 1920), 'height': random.randint(800, 1080)},
            user_agent=self.config.USER_AGENT,
            java_script_enabled=True
        )
        
        await context.add_init_script(self.config.STEALTH_JS)
        
        return playwright, browser, context
    
    async def handle_popups(self, page):
        """Xử lý các popup có thể xuất hiện"""
        try:
            for selector in self.config.POPUP_SELECTORS:
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
        
        scroll_pause_time = 2.0
        scroll_height = await page.evaluate("document.body.scrollHeight")
        current_scroll_position = 0
        scroll_step = 300
        
        while current_scroll_position < scroll_height:
            current_scroll_position += scroll_step
            await page.evaluate(f"window.scrollTo(0, {current_scroll_position})")
            await page.wait_for_timeout((scroll_pause_time + random.random()) * 1000)
            
            new_scroll_height = await page.evaluate("document.body.scrollHeight")
            if new_scroll_height > scroll_height:
                scroll_height = new_scroll_height
                
            if current_scroll_position > 5000:
                break
    
    async def save_debug_info(self, page, filename_prefix="debug"):
        """Lưu thông tin debug"""
        try:
            screenshot_path = os.path.join(self.config.SCREENSHOTS_DIR, f"{filename_prefix}_screenshot.png")
            await page.screenshot(path=screenshot_path)
            
            html_path = os.path.join(self.config.LOGS_DIR, f"{filename_prefix}_content.html")
            html = await page.content()
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"Đã lưu thông tin debug: {screenshot_path} và {html_path}")
        except Exception as e:
            print(f"Lỗi khi lưu thông tin debug: {e}")
    
    async def save_error_info(self, page, error, current_page=None):
        """Lưu thông tin lỗi"""
        try:
            page_info = f"_page{current_page}" if current_page else ""
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            screenshot_path = os.path.join(self.config.ERRORS_DIR, f"error{page_info}_{timestamp}.png")
            await page.screenshot(path=screenshot_path)
            
            error_log_path = os.path.join(self.config.ERRORS_DIR, f"error{page_info}_{timestamp}.txt")
            with open(error_log_path, "w", encoding="utf-8") as f:
                f.write(f"URL: {await page.evaluate('() => window.location.href')}\n")
                f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {str(error)}\n")
            
            print(f"Đã lưu thông tin lỗi: {screenshot_path}")
        except Exception as e:
            print(f"Không thể lưu thông tin lỗi: {e}")

    async def save_partial_data(self, current_page):
        """Lưu dữ liệu tạm thời"""
        if self.data:
            print(f"Lưu dữ liệu tạm thời sau khi xử lý trang {current_page}...")
            temp_df = pd.DataFrame(self.data)
            temp_df.to_csv(self.config.OUTPUT_FILE_PARTIAL, index=False, encoding='utf-8-sig')
            print(f"Đã lưu {len(self.data)} bản ghi vào file tạm: {self.config.OUTPUT_FILE_PARTIAL}")

    async def save_final_data(self):
        """Lưu dữ liệu cuối cùng"""
        if self.data:
            df = pd.DataFrame(self.data)
            df.to_csv(self.config.OUTPUT_FILE, index=False, encoding='utf-8-sig')
            print(f"Đã lưu {len(self.data)} bản ghi vào file {self.config.OUTPUT_FILE}")
            
            print("\n5 bản ghi đầu tiên:")
            print(df.head().to_string(index=False))
            return True
        else:
            print("Không tìm thấy dữ liệu nào")
            return False
    
    # Các phương thức trừu tượng cần được triển khai ở các lớp con
    async def wait_for_list_elements(self, page):
        """Tìm các phần tử chứa dữ liệu"""
        raise NotImplementedError("Phương thức này cần được triển khai ở lớp con")
    
    async def extract_data(self, page):
        """Trích xuất dữ liệu từ trang"""
        raise NotImplementedError("Phương thức này cần được triển khai ở lớp con")
    
    async def go_to_next_page(self, page, current_page):
        """Di chuyển đến trang tiếp theo"""
        raise NotImplementedError("Phương thức này cần được triển khai ở lớp con")
    
    async def scrape(self):
        """Hàm chính để thực hiện scraping"""
        print(f"Bắt đầu scraping dữ liệu từ {self.config.SITE_NAME}...")
        
        playwright, browser, context = await self.setup_browser()
        
        try:
            page = await context.new_page()
            await page.goto(self.config.START_URL, timeout=self.config.PAGE_LOAD_TIMEOUT)
            print("Đã tải trang web thành công")
            
            await page.wait_for_timeout(self.config.INITIAL_WAIT_TIME)
            await self.handle_popups(page)
            
            current_page = 1
            
            while current_page <= self.max_pages:
                print(f"\n--- ĐANG XỬ LÝ TRANG {current_page} ---\n")
                
                try:
                    await self.auto_scroll(page)
                    await self.extract_data(page)
                    await self.save_partial_data(current_page)
                    
                    if current_page == self.max_pages:
                        break
                        
                    success = await self.go_to_next_page(page, current_page)
                    if not success:
                        print(f"Không thể chuyển sang trang {current_page + 1}, dừng việc cào dữ liệu.")
                        break
                        
                    current_page += 1
                    
                    pause_time = self.config.PAGE_PAUSE_TIME + random.random() * 3
                    print(f"Đợi {pause_time:.2f} giây trước khi xử lý trang tiếp theo...")
                    await page.wait_for_timeout(pause_time * 1000)
                    
                except Exception as e:
                    print(f"Lỗi khi xử lý trang {current_page}: {e}")
                    await self.save_error_info(page, e, current_page)
                    await self.save_partial_data(current_page)
                    
                    try:
                        await page.reload()
                        await page.wait_for_load_state('networkidle')
                        await page.wait_for_timeout(5000)
                    except:
                        break
            
            await self.save_final_data()
                
        except Exception as e:
            print(f"Lỗi trong quá trình scraping: {e}")
            await self.save_debug_info(page, "error")
        finally:
            await browser.close()
            await playwright.stop()