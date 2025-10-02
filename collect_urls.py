import asyncio
import csv
import time
from playwright.async_api import async_playwright

# --- CẤU HÌNH ---
BASE_URL_TEMPLATE = "https://oto.com.vn/mua-ban-xe/p{}"
MAX_PAGES_TO_SCAN = 100
CONCURRENT_PAGE_SCRAPES = 10
CONCURRENT_DEEP_SCRAPES = 10

OUTPUT_FILE = "final_aidxc_urls.csv"

INITIAL_LINK_SELECTOR = 'h3.title a, .title a, a[href*="/mua-ban-xe-"], .car-item h3 a, .list-car h3 a'
TARGET_LINK_SELECTOR = 'a[href*="aidxc"]'

BLOCK_RESOURCE_TYPES = ['image', 'stylesheet', 'font', 'media']

# --- GIAI ĐOẠN 1: THU THẬP URL TỐC ĐỘ CAO ---

async def scrape_links_from_single_page(browser, page_num):
    """Worker: Mở 1 trang, chặn tài nguyên, lấy link rồi đóng lại."""
    urls = set()
    page = None
    try:
        page = await browser.new_page()
        
        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCK_RESOURCE_TYPES else route.continue_())
        
        url = BASE_URL_TEMPLATE.format(page_num)
        print(f"Bắt đầu quét trang {page_num}...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        link_elements = await page.locator(INITIAL_LINK_SELECTOR).all()

        for link in link_elements:
            href = await link.get_attribute('href')
            if href and href.startswith('/'):
                full_url = "https://oto.com.vn" + href
                urls.add(full_url)
        print(f"  Trang {page_num} xong, tìm thấy {len(urls)} link.")
        return urls
    except Exception as e:
        print(f"  Lỗi ở trang {page_num}: {e}")
        return set()
    finally:
        if page:
            await page.close()

async def collect_initial_urls_in_parallel(browser):
    """Điều phối việc cào các trang danh sách một cách song song."""
    print(f"--- Bắt đầu Giai đoạn 1: Thu thập URL song song (tối đa {MAX_PAGES_TO_SCAN} trang) ---")
    
    semaphore = asyncio.Semaphore(CONCURRENT_PAGE_SCRAPES)
    
    tasks = []
    for page_num in range(1, MAX_PAGES_TO_SCAN + 1):
        async def task_wrapper(num):
            async with semaphore:
                return await scrape_links_from_single_page(browser, num)
        tasks.append(task_wrapper(page_num))

    results = await asyncio.gather(*tasks)
    
    all_urls = set()
    for url_set in results:
        all_urls.update(url_set)
        
    return list(all_urls)

# --- CÁC HÀM GIAI ĐOẠN SAU ---

async def get_target_links_from_page(browser, url, semaphore):
    """Giai đoạn 3: Truy cập một URL trung gian và cào các link chứa 'aidxc'."""
    async with semaphore:
        found_urls = set()
        page = None
        try:
            page = await browser.new_page()
            await page.route("**/*", lambda route: route.abort() if route.request.resource_type in BLOCK_RESOURCE_TYPES else route.continue_())
            print(f"    Đi sâu vào: {url[:80]}...")
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            target_links = await page.locator(TARGET_LINK_SELECTOR).all()

            for link in target_links:
                href = await link.get_attribute('href')
                if href and href.startswith('/'):
                    full_url = "https://oto.com.vn" + href
                    found_urls.add(full_url)
            return found_urls
        except Exception:
            return set()
        finally:
            if page:
                await page.close()

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        initial_urls = await collect_initial_urls_in_parallel(browser)
        
        if not initial_urls:
            print("Không thu thập được URL ban đầu nào. Dừng chương trình.")
            await browser.close()
            return
        
        print(f"\n--- Hoàn tất Giai đoạn 1: Tìm thấy {len(initial_urls)} URL ban đầu. ---\n")

        final_urls = {url for url in initial_urls if "aidxc" in url}
        intermediate_urls = [url for url in initial_urls if "aidxc" not in url]

        print("--- Bắt đầu Giai đoạn 2: Phân loại URL ---")
        print(f"Đã tìm thấy {len(final_urls)} URL cuối cùng (chứa 'aidxc').")
        print(f"Cần truy cập {len(intermediate_urls)} URL trung gian để tìm thêm.\n")

        if intermediate_urls:
            print("--- Bắt đầu Giai đoạn 3: Đi sâu vào các URL trung gian ---")
            semaphore = asyncio.Semaphore(CONCURRENT_DEEP_SCRAPES)
            tasks = [get_target_links_from_page(browser, url, semaphore) for url in intermediate_urls]
            
            results = await asyncio.gather(*tasks)
            
            newly_found_urls = set()
            for url_set in results:
                newly_found_urls.update(url_set)
            
            print(f"\n--- Hoàn tất Giai đoạn 3: Tìm thấy thêm {len(newly_found_urls)} URL cuối cùng. ---\n")
            final_urls.update(newly_found_urls)

        await browser.close()

    if final_urls:
        print(f"Thu thập hoàn tất! Tổng cộng có {len(final_urls)} URL cuối cùng chứa 'aidxc'.")
        
        with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['final_url'])
            for url in sorted(list(final_urls)):
                writer.writerow([url])
        
        print(f"Đã lưu tất cả link vào file: {OUTPUT_FILE}")
    else:
        print("\nKhông tìm thấy URL nào chứa 'aidxc'.")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"\nTổng thời gian thực thi: {end_time - start_time:.2f} giây.")