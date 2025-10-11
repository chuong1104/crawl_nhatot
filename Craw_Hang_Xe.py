import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin

async def extract_car_model_urls():
    base_url = "https://oto.com.vn"
    start_url = "https://oto.com.vn/mua-ban-xe"
    model_urls = set()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            print("Đang truy cập trang chính...")
            await page.goto(start_url)
            await page.wait_for_load_state('networkidle')
            
            # Lấy tất cả các hãng xe chính
            print("Đang tìm các hãng xe chính...")
            main_brands = await page.query_selector_all('li.item[makeid]')
            print(f"Tìm thấy {len(main_brands)} hãng xe chính")
            
            for i, brand in enumerate(main_brands, 1):
                try:
                    brand_name_elem = await brand.query_selector('a')
                    brand_name = await brand_name_elem.text_content() if brand_name_elem else f"Hãng_{i}"
                    print(f"({i}/{len(main_brands)}) Đang xử lý hãng: {brand_name.strip()}")
                    
                    await extract_brand_models(page, brand, model_urls, base_url)
                except Exception as e:
                    print(f"Lỗi khi xử lý hãng xe {brand_name}: {e}")
            
            # Xử lý các hãng xe khác - PHƯƠNG PHÁP MỚI KHÔNG CẦN HOVER
            print("\nĐang xử lý hãng xe khác...")
            await extract_other_brands_with_js(page, model_urls, base_url)
                
            print(f"\nTổng số model URL đã thu thập: {len(model_urls)}")
            
        except Exception as e:
            print(f"Lỗi chính: {e}")
        finally:
            await browser.close()
    
    return model_urls

async def extract_brand_models(page, brand_element, model_urls, base_url):
    try:
        # Hover để mở dropdown
        await brand_element.hover()
        await page.wait_for_timeout(1000)
        
        # Lấy tất cả model từ dropdown
        model_links = await brand_element.query_selector_all('li[modelid] a')
        print(f"  - Tìm thấy {len(model_links)} model")
        
        for link in model_links:
            try:
                href = await link.get_attribute('href')
                class_name = await link.get_attribute('class') or ''
                
                if (href and not href.startswith('javascript') 
                    and 'disabled-a' not in class_name
                    and '/mua-ban-xe-' in href):
                    full_url = urljoin(base_url, href)
                    model_name = await link.text_content()
                    
                    model_urls.add(full_url)
                    print(f"    ✓ {model_name.strip()}")
            except Exception as e:
                print(f"    Lỗi khi xử lý model: {e}")
    except Exception as e:
        print(f"  Lỗi khi xử lý hãng xe: {e}")

async def extract_other_brands_with_js(page, model_urls, base_url):
    """Phương pháp mới: sử dụng JavaScript để lấy tất cả URL mà không cần hover"""
    try:
        # Sử dụng JavaScript để lấy tất cả URL từ DOM
        other_brands_data = await page.evaluate("""() => {
            const results = [];
            const otherBrandsSection = document.querySelector('li.item.other.make-orther');
            if (!otherBrandsSection) return results;
            
            // Tìm tất cả link model trong phần hãng khác
            const allLinks = otherBrandsSection.querySelectorAll('a[href*="/mua-ban-xe-"]');
            
            allLinks.forEach(link => {
                const href = link.getAttribute('href');
                const className = link.getAttribute('class') || '';
                const text = link.textContent.trim();
                
                if (href && !href.startsWith('javascript') && 
                    !className.includes('disabled-a') && 
                    !href.includes('aidxc')) {
                    results.push({
                        href: href,
                        text: text
                    });
                }
            });
            
            return results;
        }""")
        
        print(f"  - Tìm thấy {len(other_brands_data)} model trong hãng khác")
        
        for item in other_brands_data:
            try:
                full_url = urljoin(base_url, item['href'])
                model_urls.add(full_url)
                print(f"    ✓ {item['text']}: {full_url}")
            except Exception as e:
                print(f"    Lỗi khi xử lý URL: {e}")
                
    except Exception as e:
        print(f"  Lỗi khi xử lý hãng khác: {e}")

async def main():
    print("Bắt đầu thu thập URL model xe từ oto.com.vn...")
    urls = await extract_car_model_urls()
    
    # Lưu kết quả
    filename = 'car_model_urls.txt'
    with open(filename, 'w', encoding='utf-8') as f:
        for url in sorted(urls):
            f.write(url + '\n')
    
    print(f"\nHoàn thành! Đã tìm thấy {len(urls)} URL model xe")
    print(f"Kết quả đã được lưu vào {filename}")
    
    # Hiển thị 10 URL đầu tiên
    print("\n10 URL đầu tiên:")
    for i, url in enumerate(sorted(urls)[:10], 1):
        print(f"{i}. {url}")

if __name__ == '__main__':
    asyncio.run(main())