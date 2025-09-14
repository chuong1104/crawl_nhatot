import os

class NhaTotConfig:
    SITE_NAME = "NhaTot"
    START_URL = 'https://www.nhatot.com/thue-bat-dong-san-ha-noi'
    HEADLESS = False
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
    
    # Thư mục lưu trữ (sẽ được cập nhật từ main.py)
    CSV_DIR = 'results/csv'
    SCREENSHOTS_DIR = 'results/screenshots'
    LOGS_DIR = 'results/logs'
    ERRORS_DIR = 'results/errors'
    
    # Tên file đầu ra
    OUTPUT_FILE = os.path.join(CSV_DIR, 'nhatot_properties2.csv')

    # Tên file tạm thời để lưu dữ liệu khi cào từng trang
    OUTPUT_FILE_PARTIAL = os.path.join(CSV_DIR, 'nhatot_properties_partial.csv')
    
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
    # Selectors cho phần tử chứa danh sách bất động sản
    PROPERTY_SELECTORS = [
        '.c15fd2pn',
        'div.c15fd2pn',
        'a[itemprop="item"]',
        'a.cqzlgv9',
        '.szp40s8',
        'div.szp40s8',
        'div:has(> h3[class*="a3f35hz"])',
        '.szp40s8.r9vw5if',
        'div.AdItem_wrapperAdItem__S6qPH',
        '.AdsList_adsListContainers__JW7pj > div',
        '.adsListBottom > div'
    ]
    # Selectors dự phòng nếu không tìm thấy phần tử với PROPERTY_SELECTORS
    FALLBACK_SELECTORS = [
        'div:has(h3):has(span[style*="color: rgb(240, 50, 94)"])',
        'div:has(h3):has(span[style*="color: rgb(34, 34, 34)"])',
        'div:has(.sqqmhlc)',
        'div:has(svg#LocationFilled)'
    ]
    
    # Chi tiết selectors 
    TITLE_SELECTORS = ['h3.a3f35hz', 'h3[class*="a1ygob26"]', 'h3', '.szp40s8 h3']
    PRICE_SELECTORS = ['span.bfe6oav[style*="color: rgb(240, 50, 94)"]', 'span[class*="t1dp97gi"]', '.sqqmhlc span:first-child']
    AREA_SELECTORS = ['span.bfe6oav[style*="color: rgb(34, 34, 34)"]', 'span[class*="t1e1b6m2"]', '.sqqmhlc span:last-child']
    LOCATION_SELECTORS = ['span.c1u6gyxh[style*="color: rgb(140, 140, 140)"]', 'span[class*="t1u18gyr"]', 'div:has(> svg#LocationFilled) + span']
    DATE_SELECTORS = ['span.c1u6gyxh[style*="color: rgb(255, 255, 255)"]', 'span[class*="tx5yyjc"]', '.m1vb9shx span']
    INFO_SELECTORS = ['span.bwq0cbs', 'span[class*="tle2ik0"]', '.szp40s8 > span']
    
    # Pagination selectors 
    PAGINATION_SELECTORS = [
        'a[href*="page={}"]',
        '.Paging_pagingItem__Y3r2u a[href*="page={}"]',
        'button.Paging_redirectPageBtn__KvsqJ:has(i.Paging_rightIcon__3p8MS)',
        'i.Paging_rightIcon__3p8MS',
        'button:has(i[class*="rightIcon"])'
    ]
    
    PAGINATION_URL_TEMPLATE = "https://www.nhatot.com/thue-bat-dong-san-ha-noi?page={}"