# Web Scraper for Oto.com.vn

Dự án web scraping thu thập dữ liệu xe ô tô từ trang web [oto.com.vn](https://oto.com.vn) - trang web mua bán xe ô tô lớn tại Việt Nam.

## Mô tả dự án

Dự án này sử dụng Python và Playwright để tự động thu thập thông tin xe ô tô từ oto.com.vn. Scraper có khả năng:

- **Tự động load more**: Xử lý nút "Hiển thị thêm" để tải tất cả dữ liệu mà không cần phân trang truyền thống
- **Trích xuất chi tiết**: Truy cập từng trang chi tiết xe để lấy đầy đủ thông tin
- **Chống trùng lặp**: Theo dõi URL đã xử lý để tránh thu thập dữ liệu trùng lặp
- **Lưu dữ liệu**: Xuất CSV với encoding UTF-8-Sig hỗ trợ tiếng Việt

## Tính năng

### Dữ liệu thu thập được
- **Thông tin cơ bản**: Tên xe, giá tiền, ngày đăng bài
- **Thông số kỹ thuật**: Năm sản xuất, nhiên liệu, kiểu dáng, tình trạng
- **Thông số vận hành**: Số km đã đi, hộp số
- **Thông tin khác**: Xuất xứ, địa điểm bán, URL gốc

### Tính năng kỹ thuật
- **Asynchronous**: Sử dụng asyncio để xử lý đồng thời, tăng tốc độ scraping
- **Stealth mode**: Sử dụng Playwright với chế độ ẩn danh để tránh bị chặn
- **Auto-retry**: Tự động thử lại khi kết nối thất bại
- **Partial saving**: Lưu dữ liệu tạm thời để tránh mất dữ liệu khi có lỗi
- **Debug tools**: Chụp ảnh màn hình và lưu HTML để debug

## Cài đặt

### Yêu cầu hệ thống
- Python 3.7+
- Playwright compatible browser

### Các bước cài đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd crawl_nhatot
```

2. **Tạo và kích hoạt môi trường ảo**
```bash
python -m venv .venv
# Trên Windows:
.venv\Scripts\activate
# Trên macOS/Linux:
source .venv/bin/activate
```

3. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

4. **Cài đặt trình duyệt cho Playwright**
```bash
python -m playwright install
```

## Sử dụng

### Chạy cơ bản
```bash
python main.py
```

### Chạy với số lần load more tùy chỉnh
```bash
# Chạy với tối đa 5 lần nhấn "Hiển thị thêm"
python main.py 5

# Chạy với tối đa 20 lần nhấn "Hiển thị thêm"
python main.py 20
```

### Cấu trúc tham số
```bash
python main.py [số_lần_load_more_tối_đa]
```
- **Mặc định**: 500 lần nếu không có tham số
- **Khuyến nghị**: 10-50 lần cho lần chạy đầu tiên để kiểm tra

## Cấu trúc dự án
```
crawl_nhatot/
├── main.py                 # Entry point chính
├── base_scraper.py         # Lớp cơ sở cho scraper
├── requirements.txt        # Danh sách dependencies
├── configs/
│   ├── __init__.py
│   └── oto_config.py       # Cấu hình cho oto.com.vn
├── scrapers/
│   ├── __init__.py
│   └── oto_scraper.py      # Scraper cụ thể cho oto.com.vn
├── utils/
│   ├── __init__.py
│   └── scraper_utils.py    # Các hàm tiện ích xử lý dữ liệu
└── results/               # Thư mục kết quả (tự động tạo)
    ├── csv/               # File CSV chứa dữ liệu
    ├── screenshots/       # Ảnh chụp màn hình debug
    ├── logs/              # File log HTML
    └── errors/            # Thông tin lỗi
```

## Định dạng dữ liệu đầu ra

File CSV kết quả có các cột sau:

| Cột | Kiểu dữ liệu | Mô tả |
|-----|--------------|-------|
| Tên xe | String | Tên đầy đủ của xe |
| Giá tiền | Number | Giá xe (số nguyên, đơn vị VND) |
| Ngày đăng bài | String | Ngày đăng tin (dd/mm/yyyy) |
| Năm sản xuất | Number | Năm sản xuất xe |
| Nhiên liệu | String | Loại nhiên liệu (Xăng/Dầu/Điện/Hybrid) |
| Kiểu dáng | String | Kiểu dáng xe (SUV/Sedan/Hatchback...) |
| Tình trạng | String | Tình trạng xe (Xe mới/Xe cũ) |
| Số km đã đi | Number | Số km đã đi (số nguyên) |
| Hộp số | String | Loại hộp số (Số tự động/Số sàn) |
| Xuất xứ | String | Xuất xứ (Nhập khẩu/Trong nước) |
| Địa điểm | String | Địa điểm bán xe |
| URL | String | URL gốc trên oto.com.vn |







