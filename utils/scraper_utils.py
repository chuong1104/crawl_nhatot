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
    if not text or text == 'N/A':
        return 'N/A'
    return re.sub(r'\s+', ' ', text).strip()

def extract_number(text):
    """Trích xuất số từ chuỗi văn bản (hỗ trợ cả dấu chấm và phẩy)"""
    if not text or text == 'N/A':
        return None
        
    # Chuẩn hóa chuỗi số: thay thế dấu phẩy bằng dấu chấm, loại bỏ ký tự không phải số và dấu chấm/phẩy
    cleaned_text = re.sub(r'[^\d.,]', '', str(text))
    
    # Nếu có cả dấu chấm và phẩy, giả sử phẩy là phần thập phân
    if ',' in cleaned_text and '.' in cleaned_text:
        cleaned_text = cleaned_text.replace('.', '').replace(',', '.')
    # Nếu chỉ có phẩy, xem như là dấu thập phân
    elif ',' in cleaned_text:
        cleaned_text = cleaned_text.replace(',', '.')
    
    # Tìm số (có thể có dấu thập phân)
    matches = re.findall(r'\d+(?:\.\d+)?', cleaned_text)
    return float(matches[0]) if matches else None

def extract_price(price_text):
    """Trích xuất giá từ chuỗi văn bản - tối ưu cho xe ô tô"""
    if not price_text or price_text == 'N/A':
        return None
        
    # Chuẩn hóa chuỗi giá
    price_text = str(price_text).lower().strip()
    
    # Loại bỏ các từ không cần thiết
    unwanted_words = ['giá', 'xe', 'ôtô', 'oto', 'bán', 'mua', ':', '-']
    for word in unwanted_words:
        price_text = price_text.replace(word, '')
    price_text = price_text.strip()
    
    # Trích xuất số
    number = extract_number(price_text)
    if not number:
        return None
    
    # Xác định đơn vị tiền tệ
    if 'tỷ' in price_text or 'tỉ' in price_text:
        return number * 1000000000
    elif 'triệu' in price_text or 'tr' in price_text:
        return number * 1000000
    elif 'nghìn' in price_text or 'k' in price_text:
        return number * 1000
    else:
        # Nếu không có đơn vị rõ ràng, giả sử là triệu nếu số nhỏ hơn 1000
        return number * 1000000 if number < 1000 else number

def format_price(price_value):
    """Định dạng giá thành chuỗi dễ đọc"""
    if not price_value:
        return "N/A"
    
    if price_value >= 1000000000:
        return f"{price_value / 1000000000:.1f} tỷ" if price_value % 1000000000 != 0 else f"{int(price_value / 1000000000)} tỷ"
    elif price_value >= 1000000:
        return f"{price_value / 1000000:.1f} triệu" if price_value % 1000000 != 0 else f"{int(price_value / 1000000)} triệu"
    elif price_value >= 1000:
        return f"{int(price_value / 1000)} nghìn"
    else:
        return f"{int(price_value)} đồng"

def extract_km(km_text):
    """Trích xuất số km từ chuỗi văn bản"""
    if not km_text or km_text == 'N/A':
        return None
        
    # Chuẩn hóa chuỗi km
    km_text = str(km_text).lower().replace('km', '').strip()
    
    # Trích xuất số (hỗ trợ định dạng 3.900 km)
    number = extract_number(km_text)
    return number

def format_km(km_value):
    """Định dạng số km thành chuỗi dễ đọc"""
    if not km_value:
        return "N/A"
    
    if km_value >= 1000000:
        return f"{km_value / 1000000:.1f} triệu km"
    elif km_value >= 1000:
        return f"{int(km_value / 1000)}.{int(km_value % 1000 / 100):01d} nghìn km" if km_value % 1000 >= 100 else f"{int(km_value / 1000)} nghìn km"
    else:
        return f"{int(km_value)} km"

def extract_year(year_text):
    """Trích xuất năm từ chuỗi văn bản"""
    if not year_text or year_text == 'N/A':
        return None
        
    # Tìm số có 4 chữ số (năm)
    matches = re.findall(r'\b(19|20)\d{2}\b', str(year_text))
    if matches:
        return int(matches[0])
    
    # Tìm bất kỳ số nào từ 1990-2030
    number = extract_number(year_text)
    if number and 1990 <= number <= 2030:
        return int(number)
    
    return None

def clean_car_name(car_name):
    """Làm sạch tên xe ô tô"""
    if not car_name or car_name == 'N/A':
        return 'N/A'
    
    # Loại bỏ năm ở đầu (ví dụ: "2024 - Lexus RX 350 Luxury" -> "Lexus RX 350 Luxury")
    cleaned = re.sub(r'^\d{4}\s*[-–]\s*', '', str(car_name))
    
    # Loại bỏ các ký tự đặc biệt và khoảng trắng thừa
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned

def extract_fuel_type(fuel_text):
    """Trích xuất và chuẩn hóa loại nhiên liệu"""
    if not fuel_text or fuel_text == 'N/A':
        return 'N/A'
    
    fuel_text = str(fuel_text).lower().strip()
    
    fuel_mapping = {
        'xăng': 'Xăng',
        'máy xăng': 'Xăng',
        'dầu': 'Dầu',
        'diesel': 'Diesel',
        'điện': 'Điện',
        'hybrid': 'Hybrid',
        'xăng hybrid': 'Xăng Hybrid',
        'điện hybrid': 'Điện Hybrid',
        'plug-in hybrid': 'Plug-in Hybrid'
    }
    
    for key, value in fuel_mapping.items():
        if key in fuel_text:
            return value
    
    return fuel_text.capitalize()

def extract_transmission(transmission_text):
    """Trích xuất và chuẩn hóa loại hộp số"""
    if not transmission_text or transmission_text == 'N/A':
        return 'N/A'
    
    transmission_text = str(transmission_text).lower().strip()
    
    transmission_mapping = {
        'số tự động': 'Số tự động',
        'tự động': 'Số tự động',
        'số sàn': 'Số sàn',
        'sàn': 'Số sàn',
        'ly hợp kép': 'Ly hợp kép',
        'dct': 'Ly hợp kép',
        'cvt': 'CVT'
    }
    
    for key, value in transmission_mapping.items():
        if key in transmission_text:
            return value
    
    return transmission_text.capitalize()

def extract_car_condition(condition_text):
    """Trích xuất và chuẩn hóa tình trạng xe"""
    if not condition_text or condition_text == 'N/A':
        return 'N/A'
    
    condition_text = str(condition_text).lower().strip()
    
    condition_mapping = {
        'xe mới': 'Xe mới',
        'mới': 'Xe mới',
        'xe cũ': 'Xe cũ',
        'cũ': 'Xe cũ',
        'đã qua sử dụng': 'Xe cũ'
    }
    
    for key, value in condition_mapping.items():
        if key in condition_text:
            return value
    
    return condition_text.capitalize()

def extract_origin(origin_text):
    """Trích xuất và chuẩn hóa xuất xứ"""
    if not origin_text or origin_text == 'N/A':
        return 'N/A'
    
    origin_text = str(origin_text).lower().strip()
    
    origin_mapping = {
        'nhập khẩu': 'Nhập khẩu',
        'trong nước': 'Trong nước',
        'lắp ráp trong nước': 'Trong nước',
        'việt nam': 'Trong nước'
    }
    
    for key, value in origin_mapping.items():
        if key in origin_text:
            return value
    
    return origin_text.capitalize()

def clean_location(location_text):
    """Làm sạch thông tin địa điểm"""
    if not location_text or location_text == 'N/A':
        return 'N/A'
    
    # Loại bỏ các từ thừa và chuẩn hóa
    location = str(location_text).replace('Tỉnh thành:', '').replace('Địa điểm:', '').strip()
    location = re.sub(r'\s+', ' ', location)
    
    return location

def extract_area(area_text):
    """Trích xuất diện tích từ chuỗi văn bản (giữ nguyên cho tương thích)"""
    if not area_text or area_text == 'N/A':
        return None
        
    number = extract_number(area_text)
    return number

# Hàm mới để chuẩn hóa toàn bộ dữ liệu xe
def normalize_car_data(car_data):
    """Chuẩn hóa toàn bộ dữ liệu xe ô tô"""
    normalized = car_data.copy()
    
    # Chuẩn hóa từng trường
    if 'title' in normalized:
        normalized['title'] = clean_car_name(normalized['title'])
    
    if 'price' in normalized and normalized['price'] != 'N/A':
        price_value = extract_price(normalized['price'])
        if price_value:
            normalized['price_value'] = price_value
            normalized['price_display'] = format_price(price_value)
        else:
            normalized['price_value'] = None
            normalized['price_display'] = 'N/A'
    
    if 'km_driven' in normalized and normalized['km_driven'] != 'N/A':
        km_value = extract_km(normalized['km_driven'])
        if km_value:
            normalized['km_value'] = km_value
            normalized['km_display'] = format_km(km_value)
        else:
            normalized['km_value'] = None
            normalized['km_display'] = 'N/A'
    
    if 'manufacture_year' in normalized and normalized['manufacture_year'] != 'N/A':
        year_value = extract_year(normalized['manufacture_year'])
        if year_value:
            normalized['manufacture_year'] = year_value
    
    if 'fuel' in normalized and normalized['fuel'] != 'N/A':
        normalized['fuel'] = extract_fuel_type(normalized['fuel'])
    
    if 'transmission' in normalized and normalized['transmission'] != 'N/A':
        normalized['transmission'] = extract_transmission(normalized['transmission'])
    
    if 'condition' in normalized and normalized['condition'] != 'N/A':
        normalized['condition'] = extract_car_condition(normalized['condition'])
    
    if 'origin' in normalized and normalized['origin'] != 'N/A':
        normalized['origin'] = extract_origin(normalized['origin'])
    
    if 'location' in normalized and normalized['location'] != 'N/A':
        normalized['location'] = clean_location(normalized['location'])
    
    if 'description' in normalized and normalized['description'] != 'N/A':
        normalized['description'] = clean_text(normalized['description'])
    
    return normalized