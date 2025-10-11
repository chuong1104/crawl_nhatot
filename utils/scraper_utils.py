import os
import re


def create_directory(directory):
    """Tạo thư mục nếu chưa tồn tại"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Đã tạo thư mục: {directory}")

def clean_filename(text):
    """Làm sạch tên file không hợp lệ"""
    return re.sub(r'[\\/*?:"<>|]', "", text)

# --- Các hàm xử lý và chuẩn hóa dữ liệu đã được loại bỏ ---
# Việc làm sạch và chuẩn hóa sẽ được thực hiện trong một script riêng (preprocess_data.py)
# sau khi đã thu thập xong toàn bộ dữ liệu thô.
# Điều này giúp tách biệt rõ ràng hai giai đoạn:
# 1. Thu thập (Scraping): Lấy dữ liệu gốc nhanh nhất có thể.
# 2. Xử lý (Processing): Làm sạch, chuẩn hóa và định dạng dữ liệu.