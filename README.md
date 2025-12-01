# Web Scraper for Oto.com.vn

Dự án web scraping thu thập dữ liệu xe ô tô từ trang web [oto.com.vn](https://oto.com.vn) - trang web mua bán xe ô tô lớn tại Việt Nam.

## Mô tả dự án

Dự án này sử dụng Python và Playwright để tự động thu thập thông tin xe ô tô từ oto.com.vn, kết quả thu được hơn 20000 xe. Quy trình được chia thành ba giai đoạn chính để tối ưu hiệu suất và độ chính xác:

1.  **Thu thập URL Hãng xe & Model (`Craw_Hang_Xe.py`)**: Tự động truy cập trang chủ, lấy URL của tất cả các danh mục hãng xe và model xe. Kết quả được lưu vào `car_model_urls.txt`.
2.  **Thu thập URL Chi tiết (`Craw_Details.py`)**: Đọc danh sách URL danh mục, sau đó quét song song qua hàng nghìn trang con để thu thập tất cả URL của các tin đăng chi tiết. Kết quả được lưu vào `car_detail_urls.txt`.
3.  **Cào dữ liệu chi tiết (`main.py`)**: Đọc danh sách URL tin đăng đã thu thập và cào dữ liệu chi tiết từ mỗi trang một cách song song, với tốc độ cao.

## Tính năng

### Dữ liệu thu thập được
- **Thông tin cơ bản**: Mã bản tin, tên xe, giá tiền, ngày đăng bài
- **Thông số kỹ thuật**: Năm sản xuất, nhiên liệu, kiểu dáng, tình trạng
- **Thông số vận hành**: Số km đã đi, hộp số
- **Thông tin khác**: Xuất xứ, địa điểm bán, URL gốc

### Tính năng kỹ thuật nâng cao
- **Multi-Stage URL Collection**: Quy trình thu thập URL 2 bước đảm bảo lấy được tối đa số lượng tin đăng trên toàn bộ trang web.
- **High-Speed Parallel Scraping**: Cào dữ liệu từ nhiều trang danh mục và trang chi tiết cùng lúc để tăng tốc độ.
- **Resource Blocking**: Chặn các tài nguyên không cần thiết (CSS, ảnh, font) để thu thập URL cực nhanh.
- **URL Deduplication**: Tự động loại bỏ các URL trùng lặp ở mỗi giai đoạn để đảm bảo dữ liệu là duy nhất.
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

Chạy các script theo đúng thứ tự sau:

### Bước 1: Thu thập URL các hãng xe và model
Chạy script này để lấy danh sách tất cả các trang danh mục xe.
```bash
python Craw_Hang_Xe.py
```
- **Đầu ra**: File `car_model_urls.txt` chứa URL của từng model xe.

### Bước 2: Thu thập URL chi tiết của từng tin đăng
Script này sẽ đọc file `car_model_urls.txt`, duyệt qua từng danh mục và các trang con để lấy URL của tất cả các tin đăng.
```bash
python Craw_Details.py
```
- **Đầu ra**: File `car_detail_urls.txt` chứa hàng chục nghìn URL chi tiết, sẵn sàng cho việc cào dữ liệu.

### Bước 3: Cào dữ liệu chi tiết từ các URL đã thu thập
Đây là bước cuối cùng, script sẽ đọc file `car_detail_urls.txt` và tiến hành cào dữ liệu song song.
```bash
python main.py
```
- **Đầu ra**: File `results/csv/oto2_com_vn_cars.csv` chứa toàn bộ dữ liệu thô đã cào được.

## Cấu trúc dự án
```
crawl_nhatot/
├── main.py                 # Giai đoạn 3: Chạy cào dữ liệu chi tiết
├── Craw_Hang_Xe.py         # Giai đoạn 1: Thu thập URL hãng xe/model
├── Craw_Details.py         # Giai đoạn 2: Thu thập URL tin đăng chi tiết
├── base_scraper.py         # Lớp cơ sở cho scraper
├── requirements.txt        # Danh sách dependencies
├── README.md               # Tài liệu này
├── car_model_urls.txt      # Output của Giai đoạn 1
├── car_detail_urls.txt     # Output của Giai đoạn 2
├── configs/
│   └── oto_config.py       # Cấu hình selectors, URL, và các tham số
├── scrapers/
│   └── oto_scraper.py      # Logic cào dữ liệu chi tiết (sử dụng trong main.py)
├── utils/
│   └── scraper_utils.py    # Các hàm tiện ích
└── results/                # Thư mục kết quả (tự động tạo)
    ├── csv/                # File CSV chứa dữ liệu
    ├── screenshots/        # Ảnh chụp màn hình debug
    ├── logs/               # File log HTML
    └── errors/             # Thông tin lỗi và debug
```

## Định dạng dữ liệu đầu ra

File CSV kết quả (`oto2_com_vn_cars.csv`) có các cột sau:

| Cột | Kiểu dữ liệu | Mô tả | Ví dụ |
|-----|--------------|-------|-------|
| ad_id | String | Mã tin đăng duy nhất | "23372753" |
| title | String | Tên đầy đủ của xe | "Toyota Camry 2.5Q" |
| price | String | Giá xe (dạng thô) | "1 tỉ 250 triệu" |
| date_posted | String | Ngày đăng tin | "13/10/2025" |
| manufacture_year | String | Năm sản xuất xe | "2020" |
| fuel | String | Loại nhiên liệu | "Xăng" |
| body_style | String | Kiểu dáng xe | "Sedan" |
| condition | String | Tình trạng xe | "Xe cũ" |
| km_driven | String | Số km đã đi (dạng thô) | "25.000 km" |
| transmission | String | Loại hộp số | "Số tự động" |
| origin | String | Xuất xứ | "Nhập khẩu" |
| location | String | Địa điểm bán xe | "Hà Nội" |
| url | String | URL gốc của tin đăng | "https://oto.com.vn/..." |
