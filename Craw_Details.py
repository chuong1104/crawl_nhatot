import asyncio
from playwright.async_api import async_playwright, Error
from urllib.parse import urljoin
import time

# --- Cấu hình ---
CONCURRENCY_LIMIT = 5  # Số lượng danh mục xử lý đồng thời. Tăng/giảm tùy theo cấu hình máy và mạng.
MAX_PAGES_PER_CATEGORY = 100 # Giới hạn số trang để tránh vòng lặp vô hạn
PAGE_TIMEOUT = 30000 # Thời gian chờ tối đa cho một trang (ms)
RESOURCES_TO_BLOCK = ["stylesheet", "image", "font", "media"] # Bỏ 'script' nếu trang cần JS để render

async def block_unnecessary_resources(route):
    """Chặn các tài nguyên không cần thiết để tăng tốc độ."""
    if route.request.resource_type in RESOURCES_TO_BLOCK:
        await route.abort()
    else:
        await route.continue_()

async def extract_cars_from_category(page, category_url, base_url):
    """Trích xuất tất cả URL xe từ một danh mục bằng cách truy cập trực tiếp vào các trang."""
    car_urls = set()
    page_num = 1

    while page_num <= MAX_PAGES_PER_CATEGORY:
        try:
            current_url = f"{category_url}/p{page_num}" if page_num > 1 else category_url
            
            try:
                await page.goto(current_url, wait_until='domcontentloaded', timeout=PAGE_TIMEOUT)
            except Error as e:
                print(f"    Lỗi khi truy cập trang {page_num} ({current_url}). Có thể đã hết trang. Lỗi: {e}")
                break

            # Trích xuất các URL xe từ trang hiện tại
            page_car_urls = await extract_car_urls_from_page(page, base_url)
            
            # Nếu không tìm thấy URL nào, coi như hết dữ liệu và dừng lại
            if not page_car_urls:
                print(f"    Không tìm thấy xe nào trên trang {page_num}, kết thúc danh mục.")
                break
            
            new_urls_found = len(page_car_urls - car_urls)
            if new_urls_found == 0 and page_num > 1:
                print(f"    Trang {page_num} không có xe mới, kết thúc danh mục.")
                break

            car_urls.update(page_car_urls)
            print(f"    Trang {page_num}: tìm thấy {new_urls_found} xe mới. Tổng số: {len(car_urls)}")
            
            page_num += 1
            await asyncio.sleep(0.5) # Thêm một khoảng nghỉ ngắn giữa các trang
            
        except Exception as e:
            print(f"    Lỗi không xác định khi xử lý trang {page_num} ({current_url}): {e}")
            break
    
    return car_urls

async def extract_car_urls_from_page(page, base_url):
    """Trích xuất tất cả URL xe từ trang hiện tại."""
    try:
        car_links = await page.query_selector_all('a[href*="aidxc"]')
        if not car_links:
            return set()

        car_urls = set()
        for link in car_links:
            href = await link.get_attribute('href')
            if href:
                full_url = urljoin(base_url, href)
                car_urls.add(full_url)
        return car_urls
    except Exception as e:
        print(f"    Lỗi khi trích xuất URL xe: {e}")
        return set()

async def worker(semaphore, context, category_url, base_url, progress):
    """Một worker để xử lý một danh mục URL."""
    async with semaphore:
        page = await context.new_page()
        # Chặn tài nguyên không cần thiết
        await page.route("**/*", block_unnecessary_resources)
        try:
            print(f"({progress}) Bắt đầu xử lý danh mục: {category_url}")
            found_urls = await extract_cars_from_category(page, category_url, base_url)
            print(f"({progress}) Hoàn thành danh mục: {category_url}. Tìm thấy {len(found_urls)} xe.")
            return found_urls
        except Exception as e:
            print(f"Lỗi nghiêm trọng trong worker cho {category_url}: {e}")
            return set()
        finally:
            await page.close()

async def main():
    print("Bắt đầu thu thập URL xe từ các danh mục...")
    start_time = time.time()
    
    base_url = "https://oto.com.vn"
    try:
        with open('car_model_urls.txt', 'r', encoding='utf-8') as f:
            category_urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file 'car_model_urls.txt'. Vui lòng chạy script thu thập danh mục trước.")
        return

    all_car_urls = set()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        tasks = []
        total_categories = len(category_urls)
        for i, category_url in enumerate(category_urls, 1):
            progress_str = f"{i}/{total_categories}"
            tasks.append(worker(semaphore, context, category_url, base_url, progress_str))
            
        results = await asyncio.gather(*tasks)
        
        for url_set in results:
            all_car_urls.update(url_set)
            
        await browser.close()

    # Lưu kết quả
    filename = 'car_detail_urls.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for url in sorted(all_car_urls):
            f.write(url + '\n')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\nHoàn thành! Đã thu thập được {len(all_car_urls)} URL xe chi tiết")
    print(f"Thời gian thực hiện: {elapsed_time:.2f} giây")
    print(f"Kết quả đã được lưu vào {filename}")
    
    # Hiển thị 10 URL đầu tiên
    if all_car_urls:
        print("\n10 URL đầu tiên:")
        for i, url in enumerate(sorted(all_car_urls)[:10], 1):
            print(f"{i}. {url}")

if __name__ == '__main__':
    asyncio.run(main())