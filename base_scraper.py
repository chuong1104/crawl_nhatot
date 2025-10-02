import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import time
import random
import os
from utils import create_directory, clean_filename

class BaseScraper:
    def __init__(self, config, max_pages):
        self.config = config
        self.data = []
        self.max_pages = max_pages # Giữ lại để tương thích, không còn nhiều ý nghĩa
        
    async def setup_browser(self):
        """Thiết lập trình duyệt với các tùy chọn cần thiết"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=self.config.HEADLESS,
            args=self.config.BROWSER_ARGS
        )
        context = await browser.new_context(
            user_agent=self.config.USER_AGENT,
            java_script_enabled=True
        )
        await context.add_init_script(self.config.STEALTH_JS)
        return playwright, browser, context
    
    async def save_debug_info(self, page, filename_prefix="debug"):
        """Lưu thông tin debug khi có lỗi."""
        try:
            # Sử dụng clean_filename từ utils
            safe_filename = clean_filename(filename_prefix)
            screenshot_path = os.path.join(self.config.SCREENSHOTS_DIR, f"{safe_filename}_screenshot.png")
            await page.screenshot(path=screenshot_path)
            
            html_path = os.path.join(self.config.LOGS_DIR, f"{safe_filename}_content.html")
            html = await page.content()
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"Đã lưu thông tin debug: {screenshot_path} và {html_path}")
        except Exception as e:
            print(f"Lỗi khi lưu thông tin debug: {e}")
    
    async def save_error_info(self, page, error, current_page=None):
        """Lưu thông tin lỗi khi có lỗi."""
        try:
            page_info = f"_page{current_page}" if current_page else ""
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Sử dụng clean_filename từ utils
            safe_filename = clean_filename(f"error{page_info}_{timestamp}")
            
            screenshot_path = os.path.join(self.config.ERRORS_DIR, f"{safe_filename}.png")
            await page.screenshot(path=screenshot_path)
            
            error_log_path = os.path.join(self.config.ERRORS_DIR, f"{safe_filename}.txt")
            with open(error_log_path, "w", encoding="utf-8") as f:
                f.write(f"URL: {await page.evaluate('() => window.location.href')}\n")
                f.write(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Error: {str(error)}\n")
            
            print(f"Đã lưu thông tin lỗi: {screenshot_path}")
        except Exception as e:
            print(f"Không thể lưu thông tin lỗi: {e}")
    async def save_partial_data(self, batch_name):
        """Lưu dữ liệu tạm thời."""
        if not self.data:
            return
        print(f"Lưu dữ liệu tạm thời cho batch '{batch_name}'...")
        df = pd.DataFrame(self.data)
        
        column_mapping = {
            'ad_id': 'Mã bản tin', 'title': 'Tên xe', 'price': 'Giá tiền',
            'date_posted': 'Ngày đăng bài', 'manufacture_year': 'Năm sản xuất',
            'fuel': 'Nhiên liệu', 'body_style': 'Kiểu dáng', 'condition': 'Tình trạng',
            'km_driven': 'Số km đã đi', 'transmission': 'Hộp số', 'origin': 'Xuất xứ',
            'location': 'Địa điểm', 'url': 'URL'
        }
        
        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())].rename(columns=available_cols)
        
        df.to_csv(self.config.OUTPUT_FILE_PARTIAL, index=False, encoding='utf-8-sig')
        print(f"Đã lưu {len(self.data)} bản ghi vào file tạm: {self.config.OUTPUT_FILE_PARTIAL}")

    async def save_final_data(self):
        """Lưu dữ liệu cuối cùng."""
        if not self.data:
            print("Không có dữ liệu để lưu.")
            return False
            
        df = pd.DataFrame(self.data)
        column_mapping = {
            'ad_id': 'Mã bản tin', 
            'title': 'Tên xe', 
            'price': 'Giá tiền',
            'date_posted': 'Ngày đăng bài', 
            'manufacture_year': 'Năm sản xuất',
            'fuel': 'Nhiên liệu', 
            'body_style': 'Kiểu dáng', 
            'condition': 'Tình trạng',
            'km_driven': 'Số km đã đi', 
            'transmission': 'Hộp số', 
            'origin': 'Xuất xứ',
            'location': 'Địa điểm', 
            'url': 'URL'
        }
        
        available_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(available_cols.keys())].rename(columns=available_cols)
        
        if 'Mã bản tin' in df.columns:
            df = df.drop_duplicates(subset=['Mã bản tin'], keep='first')
            print(f"Đã loại bỏ các bản ghi trùng lặp, còn lại {len(df)} bản ghi.")
        
        df.to_csv(self.config.OUTPUT_FILE, index=False, encoding='utf-8-sig')
        print(f"Đã lưu {len(df)} bản ghi vào file {self.config.OUTPUT_FILE}")
        
        print("\n5 bản ghi đầu tiên:")
        print(df.head().to_string(index=False))
        return True
    
    async def scrape(self):
        """Phương thức chính để thực hiện scraping, sẽ được lớp con ghi đè."""
        raise NotImplementedError("Phương thức 'scrape' phải được triển khai ở lớp con.")