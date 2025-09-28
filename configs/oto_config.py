import os

class OtoComVnConfig:
    SITE_NAME = "OtoComVn"
    START_URL = 'https://oto.com.vn/mua-ban-xe'
    HEADLESS = False
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    
    # Thư mục lưu trữ
    CSV_DIR = 'results/csv'
    SCREENSHOTS_DIR = 'results/screenshots'
    LOGS_DIR = 'results/logs'
    ERRORS_DIR = 'results/errors'
    
    # Tên file đầu ra
    OUTPUT_FILE = os.path.join(CSV_DIR, 'oto2_com_vn_cars.csv')
    OUTPUT_FILE_PARTIAL = os.path.join(CSV_DIR, 'oto2_com_vn_cars_partial.csv')
    
    BROWSER_ARGS = [
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        '--disable-blink-features=AutomationControlled',
        '--disable-web-security',
        '--disable-features=IsolateOrigins,site-per-process'
    ]

    STEALTH_JS = """
        delete navigator.__proto__.webdriver;
        window.chrome = {runtime: {}};
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });
    """
    
    PAGE_LOAD_TIMEOUT = 90000
    INITIAL_WAIT_TIME = 8000
    PAGE_PAUSE_TIME = 3
    
    # Selectors cho popup chấp nhận cookie
    POPUP_SELECTORS = [
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
    
    # Selectors cho danh sách xe
    PROPERTY_SELECTORS = [
        'h3.title a',
        '.title a',
        'a[href*="/mua-ban-xe-"]',
        '.car-item h3 a',
        '.list-car h3 a'
    ]
    
    FALLBACK_SELECTORS = [
        'a[title*="Bán xe"]',
        'a[href*="/mua-ban-xe"]'
    ]
    
    # Selectors cho nút "Hiển thị thêm"
    LOAD_MORE_SELECTOR = "span.btn-loadmore[onclick*='ListAuto.getData']"
    # SHOW_MORE_DESCRIPTION_SELECTOR = "button.btn-show.btn-show-colspan" 
    
    # Selectors cho giá xe (cập nhật dựa trên HTML mới)
    PRICE_SELECTORS = [
    'span.price',
    'p.price',
    '.price',
    '.info-right .price',
    'div.price',
    'p.price.redprice',
    'span.price.redprice',
    '.vehicle-price',
    '.cost'
    ]
    
    # Selectors cho ngày đăng bài
    DATE_POSTED_SELECTORS = [
        '.date',
        '.time',
        '.post-date',
        '[class*="date"]'
    ]
    
    # Selectors cho thông tin chi tiết xe
    DETAIL_SELECTORS = {
        'manufacture_year': 'li:has(label.label:has-text("Năm SX"))',
        'fuel': 'li:has(label.label:has-text("Nhiên liệu"))',
        'body_style': 'li:has(label.label:has-text("Kiểu dáng"))',
        'condition': 'li:has(label.label:has-text("Tình trạng"))',
        'km_driven': 'li:has(label.label:has-text("Km đã đi"))',
        'transmission': 'li:has(label.label:has-text("Hộp số"))',
        'origin': 'li:has(label.label:has-text("Xuất xứ"))',
        'location': 'li:has(label.label:has-text("Tỉnh thành"))'
    }
    
    # DESCRIPTION_SELECTOR = '.content-description, .description, [class*="description"]'
    
    # Selectors cho tiêu đề xe trong trang chi tiết
    TITLE_SELECTORS = [
        'h1',
        '.title',
        '[class*="title"]'
    ]
    
    # Pagination selectors
    PAGINATION_SELECTORS = [
        'a[href*="/mua-ban-xe/p{}"]',
        'a[href*="page={}"]',
        'a[href*="trang-{}"]',
        'a:has-text("{}")',
        'a.pagination-next',
        'a.next'
    ]
    # Selectors cho nút "Hiển thị thêm"
    LOAD_MORE_SELECTOR = "span.btn-loadmore[onclick='ListAuto.getData()']"

    PAGINATION_URL_TEMPLATE = "https://oto.com.vn/mua-ban-xe/p{}"