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

def clean_text(text):
    """Làm sạch văn bản, loại bỏ khoảng trắng thừa"""
    return re.sub(r'\s+', ' ', text).strip()

def extract_number(text):
    """Trích xuất số từ chuỗi văn bản"""
    matches = re.findall(r'\d+(?:\.\d+)?', text.replace(',', '.'))
    return float(matches[0]) if matches else None

def extract_price(price_text):
    """Trích xuất giá từ chuỗi văn bản"""
    if not price_text or price_text.lower() == 'n/a':
        return None
        
    number = extract_number(price_text)
    
    if 'tỷ' in price_text.lower():
        return number * 1000000000 if number else None
    elif 'triệu' in price_text.lower():
        return number * 1000000 if number else None
    elif 'nghìn' in price_text.lower():
        return number * 1000 if number else None
    else:
        return number
        
def extract_area(area_text):
    """Trích xuất diện tích từ chuỗi văn bản"""
    if not area_text or area_text.lower() == 'n/a':
        return None
        
    number = extract_number(area_text)
    return number