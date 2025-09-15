# Crawl_NhaTot

## Mô tả
Dự án này dùng để cào dữ liệu bất động sản từ trang [nhatot.com](https://www.nhatot.com/thue-bat-dong-san-ha-noi) và lưu kết quả ra file CSV.

## Cấu trúc thư mục
```
base_scraper.py
main.py
configs/
    nhatot_config.py
scrapers/
    nhatot_scraper.py
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

- Thay đổi số trang muốn cào trong hàm main.py
# Tùy chọn số trang tối đa để cào
    max_pages = 2

### 3. Kết quả
- Dữ liệu sẽ được lưu tại `results/csv/nhatot_properties2.csv`.
- Ảnh chụp màn hình, log và lỗi sẽ lưu trong các thư mục con của `results/`.

## Tùy chỉnh cho website khác
- Tạo file config mới trong `configs/`.
- Tạo scraper mới kế thừa [`BaseScraper`](base_scraper.py).
- Sửa lại phần import và khởi tạo trong [main.py](main.py).

## Liên hệ
Nếu có vấn đề, vui lòng liên hệ qua email hoặc mở issue trên GitHub.