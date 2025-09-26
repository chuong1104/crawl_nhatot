# Crawl_NhaTot

## Mô tả
Dự án này dùng để cào dữ liệu xe ô tô từ trang [oto.com.vn](https://oto.com.vn/mua-ban-xe) và lưu kết quả ra file CSV.

## Cấu trúc thư mục
```
base_scraper.py
main.py
configs/
    oto_config.py
scrapers/
    oto_scraper.py
utils/
    scraper_utils.py
results/
    csv/
    screenshots/
    logs/
    errors/
```

## Hướng dẫn sử dụng

### 1. Cài đặt các thư viện cần thiết
```sh
pip install playwright pandas
python -m playwright install
```

### 2. Chạy chương trình

- Thay đổi số trang muốn cào trong hàm main.py hoặc truyền tham số dòng lệnh
- Tùy chọn số trang tối đa để cào:
```python
max_pages = 100  # Mặc định cào 100 trang
```

- Chạy với số trang tùy chỉnh:
```sh
python main.py 5  # Cào 5 trang đầu tiên
```

### 3. Kết quả
- Dữ liệu sẽ được lưu tại `results/csv/oto_com_vn_cars.csv`.
- File tạm thời sẽ được lưu tại `results/csv/oto_com_vn_cars_partial.csv`.
- Ảnh chụp màn hình, log và lỗi sẽ lưu trong các thư mục con của `results/`.

## Dữ liệu thu thập
Chương trình sẽ thu thập các thông tin sau của mỗi xe:
- Tên xe
- Giá tiền
- Ngày đăng bài
- Năm sản xuất
- Nhiên liệu
- Kiểu dáng
- Tình trạng
- Số km đã đi
- Hộp số
- Xuất xứ
- Địa điểm
- URL

## Tính năng
- Tự động xử lý popup và cookie consent
- Tự động scroll và load thêm dữ liệu
- Xử lý nút "Hiển thị thêm" để tải tất cả xe trên trang
- Lưu dữ liệu tạm thời sau mỗi trang
- Chuẩn hóa dữ liệu (giá, km, năm sản xuất, v.v.)
- Tên cột tiếng Việt trong file CSV đầu ra
- Xử lý lỗi và lưu screenshot khi có vấn đề

## Tùy chỉnh cho website khác
- Tạo file config mới trong `configs/`.
- Tạo scraper mới kế thừa [`BaseScraper`](base_scraper.py).
- Sửa lại phần import và khởi tạo trong [main.py](main.py).

## Liên hệ
Nếu có vấn đề, vui lòng liên hệ qua email hoặc mở issue trên GitHub.
