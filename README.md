# Web Scraper for Oto.com.vn

Dự án web scraping thu thập dữ liệu xe ô tô từ trang web [oto.com.vn](https://oto.com.vn) - trang web mua bán xe ô tô lớn tại Việt Nam.

## Mô tả dự án

Dự án này sử dụng Python và Playwright để tự động thu thập thông tin xe ô tô từ oto.com.vn. Quy trình được chia thành hai giai đoạn chính để tối ưu hiệu suất:

1.  **Thu thập URL (`collect_urls.py`)**: Quét song song hàng trăm trang danh sách với tốc độ cao để thu thập tất cả các URL của các tin đăng chi tiết.
2.  **Cào dữ liệu chi tiết (`main.py`)**: Đọc danh sách URL đã thu thập và cào dữ liệu chi tiết từ mỗi trang một cách song song.

## Tính năng

### Dữ liệu thu thập được
- **Thông tin cơ bản**: Mã bản tin, tên xe, giá tiền, ngày đăng bài
- **Thông số kỹ thuật**: Năm sản xuất, nhiên liệu, kiểu dáng, tình trạng
- **Thông số vận hành**: Số km đã đi, hộp số
- **Thông tin khác**: Xuất xứ, địa điểm bán, URL gốc

### Tính năng kỹ thuật nâng cao
- **High-Speed URL Collection**: Quét song song nhiều trang danh sách và chặn các tài nguyên không cần thiết (CSS, ảnh, font) để thu thập URL cực nhanh.
- **Parallel Scraping**: Cào dữ liệu từ nhiều trang chi tiết cùng lúc để tăng tốc độ.
- **URL Deduplication**: Tự động loại bỏ các URL trùng lặp để đảm bảo mỗi tin đăng chỉ được xử lý một lần.
- **Stealth Mode**: Sử dụng Playwright với các tùy chỉnh để tránh bị phát hiện và chặn.
- **Intelligent Retry**: Tự động thử lại khi kết nối thất bại.
- **Batch Saving**: Lưu dữ liệu tạm thời để tránh mất mát khi xử lý số lượng lớn.
- **Error Recovery**: Tiếp tục scraping ngay cả khi một số trang bị lỗi.
- **Debug Tools**: Chụp ảnh màn hình và lưu HTML để debug khi có lỗi.

## Cài đặt

### Yêu cầu hệ thống
- Python 3.8+ (khuyến nghị Python 3.10+)
- Playwright compatible browser (tự động cài đặt)

### Các bước cài đặt

1.  **Clone repository**
    ```bash
    git clone <repository-url>
    cd crawl_nhatot
    ```

2.  **Tạo và kích hoạt môi trường ảo**
    ```bash
    python -m venv .venv
    # Trên Windows:
    .venv\Scripts\activate
    # Trên macOS/Linux:
    source .venv/bin/activate
    ```

3.  **Cài đặt dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cài đặt trình duyệt cho Playwright**
    ```bash
    python -m playwright install chromium
    ```

## Sử dụng

### Chạy cơ bản
```bash
python main.py
```
*Mặc định sẽ thử tối đa 500 lần nhấn "Hiển thị thêm" hoặc cho đến khi hết dữ liệu*

### Chạy với số lần load more tùy chỉnh
```bash
# Chạy với tối đa 5 lần nhấn "Hiển thị thêm"
python main.py 5

# Chạy với tối đa 20 lần nhấn "Hiển thị thêm" 
python main.py 20

# Chạy với tối đa 100 lần (thu thập nhiều dữ liệu)
python main.py 100
```

### Cấu trúc tham số
```bash
python main.py [số_lần_load_more_tối_đa]
```

## Cấu trúc dự án
```
crawl_nhatot/
├── main.py                 # Entry point chính
├── base_scraper.py         # Lớp cơ sở cho scraper
├── requirements.txt        # Danh sách dependencies
├── README.md               # Tài liệu này
├── configs/
│   ├── __init__.py
│   └── oto_config.py       # Cấu hình selectors, URL, và các tham số
├── scrapers/
│   ├── __init__.py
│   └── oto_scraper.py      # Logic cào dữ liệu chi tiết
├── utils/
│   ├── __init__.py
│   └── scraper_utils.py    # Các hàm tiện ích (làm sạch, chuẩn hóa)
└── results/                # Thư mục kết quả (tự động tạo)
    ├── csv/                # File CSV chứa dữ liệu
    │   ├── oto2_com_vn_cars.csv         # File dữ liệu thô
    │   ├── oto_cars_cleaned.csv         # File dữ liệu đã làm sạch
    │   └── oto2_com_vn_cars_partial.csv # File backup tạm thời
    ├── screenshots/        # Ảnh chụp màn hình debug
    ├── logs/              # File log HTML
    └── errors/            # Thông tin lỗi và debug
```

## Định dạng dữ liệu đầu ra

File CSV kết quả có các cột sau:

| Cột | Kiểu dữ liệu | Mô tả | Ví dụ |
|-----|--------------|-------|-------|
| Tên xe | String | Tên đầy đủ của xe | "Toyota Camry 2.5Q" |
| Giá tiền | Number | Giá xe (số nguyên, VND) | 1250000000 |
| Ngày đăng bài | String | Ngày đăng tin | "15/09/2025" |
| Năm sản xuất | Number | Năm sản xuất xe | 2020 |
| Nhiên liệu | String | Loại nhiên liệu | "Xăng" |
| Kiểu dáng | String | Kiểu dáng xe | "Sedan" |
| Tình trạng | String | Tình trạng xe | "Xe cũ" |
| Số km đã đi | Number | Số km đã đi | 25000 |
| Hộp số | String | Loại hộp số | "Số tự động" |
| Xuất xứ | String | Xuất xứ | "Nhập khẩu" |
| Địa điểm | String | Địa điểm bán xe | "Hà Nội" |
| Mô tả | String | Mô tả chi tiết | "Xe gia đình sử dụng..." |
| URL | String | URL gốc | "https://oto.com.vn/..." |


- cào toàn bộ link rồi xử lý trùng 1 lần cuối cùng
- chạy cùng lúc nhiều trang, chỉ lấy ra hmtl
