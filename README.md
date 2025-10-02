# Web Scraper for Oto.com.vn

Dự án web scraping thu thập dữ liệu xe ô tô từ trang web [oto.com.vn](https://oto.com.vn) - trang web mua bán xe ô tô lớn tại Việt Nam.

## Mô tả dự án

Dự án này sử dụng Python và Playwright để tự động thu thập thông tin xe ô tô từ oto.com.vn. Scraper có khả năng:

- **Tự động load more**: Xử lý nút "Hiển thị thêm" để tải tất cả dữ liệu mà không cần phân trang truyền thống
- **Phát hiện dữ liệu trùng lặp**: Dừng tự động khi không còn dữ liệu mới sau 3 lần liên tiếp
- **Trích xuất chi tiết**: Truy cập từng trang chi tiết xe để lấy đầy đủ thông tin
- **Chống trùng lặp**: Theo dõi URL đã xử lý để tránh thu thập dữ liệu trùng lặp
- **Xử lý lỗi thông minh**: Auto-retry với 3 lần thử lại cho mỗi trang
- **Lưu dữ liệu an toàn**: Xuất CSV với encoding UTF-8-Sig hỗ trợ tiếng Việt, lưu tạm mỗi 10 xe

## Tính năng

### Dữ liệu thu thập được
- **Thông tin cơ bản**: Tên xe, giá tiền, ngày đăng bài
- **Thông số kỹ thuật**: Năm sản xuất, nhiên liệu, kiểu dáng, tình trạng
- **Thông số vận hành**: Số km đã đi, hộp số
- **Thông tin khác**: Xuất xứ, địa điểm bán, mô tả, URL gốc

### Tính năng kỹ thuật nâng cao
- **Smart Load More**: Tự động dừng khi phát hiện không còn dữ liệu mới (3 lần liên tiếp)
- **URL Deduplication**: Sử dụng set để theo dõi URL đã xử lý, tránh trùng lặp
- **Asynchronous Processing**: Sử dụng asyncio để xử lý đồng thời, tăng tốc độ scraping
- **Stealth Mode**: Sử dụng Playwright với chế độ ẩn danh để tránh bị chặn
- **Intelligent Retry**: Tự động thử lại 3 lần khi kết nối thất bại với delay tăng dần
- **Batch Saving**: Lưu dữ liệu tạm thời mỗi 10 xe để tránh mất dữ liệu
- **Error Recovery**: Tiếp tục scraping ngay cả khi một số trang bị lỗi
- **Debug Tools**: Chụp ảnh màn hình và lưu HTML để debug khi có lỗi

### Cải tiến về hiệu suất
- **Efficient URL Collection**: Thu thập tất cả URL trước, sau đó xử lý chi tiết
- **Memory Optimization**: Sử dụng set() cho URL tracking thay vì list
- **Network Optimization**: Chờ 'networkidle' để đảm bảo trang tải hoàn toàn
- **Resource Management**: Tự động đóng tab sau mỗi lần xử lý để tiết kiệm bộ nhớ

## Cài đặt

### Yêu cầu hệ thống
- Python 3.8+ (khuyến nghị Python 3.10+)
- Playwright compatible browser (tự động cài đặt)

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
├── README.md              # Tài liệu này
├── configs/
│   ├── __init__.py
│   └── oto_config.py       # Cấu hình selectors và timeout
├── scrapers/
│   ├── __init__.py
│   └── oto_scraper.py      # Scraper với logic load more thông minh
├── utils/
│   ├── __init__.py
│   └── scraper_utils.py    # Các hàm tiện ích xử lý dữ liệu
└── results/               # Thư mục kết quả (tự động tạo)
    ├── csv/               # File CSV chứa dữ liệu
    │   ├── oto2_com_vn_cars.csv         # File chính
    │   └── oto2_com_vn_cars_partial.csv # File backup tạm thời
    ├── screenshots/       # Ảnh chụp màn hình debug
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
