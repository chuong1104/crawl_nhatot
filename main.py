import asyncio
import sys
import os
from scrapers import NhaTotScraper
from configs import NhaTotConfig
from utils import create_directory

async def main():
    # Tạo cấu trúc thư mục để lưu trữ kết quả và logs
    base_dir = 'results'
    
    # Chỉ tạo thư mục nếu chưa tồn tại
    if not os.path.exists(base_dir):
        create_directory(base_dir)
        print(f"Đã tạo thư mục: {base_dir}")
    
    # Tạo các thư mục con (nếu chưa tồn tại)
    csv_dir = os.path.join(base_dir, 'csv')
    screenshots_dir = os.path.join(base_dir, 'screenshots')
    logs_dir = os.path.join(base_dir, 'logs')
    errors_dir = os.path.join(base_dir, 'errors')
    
    # Chỉ tạo thư mục nếu chưa tồn tại
    for directory in [csv_dir, screenshots_dir, logs_dir, errors_dir]:
        if not os.path.exists(directory):
            create_directory(directory)
            print(f"Đã tạo thư mục: {directory}")
        else:
            print(f"Thư mục đã tồn tại, bỏ qua: {directory}")
    
    # Tạo config với các đường dẫn thư mục
    config = NhaTotConfig()
    config.CSV_DIR = csv_dir
    config.SCREENSHOTS_DIR = screenshots_dir
    config.LOGS_DIR = logs_dir
    config.ERRORS_DIR = errors_dir
    
    # Tùy chọn số trang tối đa để cào
    max_pages = 2
    if len(sys.argv) > 1:
        try:
            max_pages = int(sys.argv[1])
        except ValueError:
            print(f"Tham số không hợp lệ: {sys.argv[1]}")

    # Tạo và chạy scraper
    scraper = NhaTotScraper(config, max_pages=max_pages)
    await scraper.scrape()

if __name__ == "__main__":
    asyncio.run(main())