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
    """Trích xuất giá thành số nguyên từ chuỗi văn bản"""
    if not price_text or price_text == 'N/A':
        return None
        
    # Chuẩn hóa chuỗi giá
    price_text = str(price_text).lower().strip()
    
    # Loại bỏ các từ không cần thiết
    unwanted_words = ['giá', 'xe', 'ôtô', 'oto', 'bán', 'mua', ':', '-', 'vnd', 'đồng', 'vnđ', 'redprice']
    for word in unwanted_words:
        price_text = price_text.replace(word, '')
    price_text = re.sub(r'\s+', ' ', price_text).strip()
    
    # Xử lý các trường hợp đặc biệt
    if 'liên hệ' in price_text or 'thỏa thuận' in price_text:
        return None
    
    # Xử lý định dạng "X tỉ Y triệu"
    if 'tỷ' in price_text or 'tỉ' in price_text:
        # Tách thành phần tỷ và triệu
        billion_part = 0
        million_part = 0
        
        # Tìm phần tỷ
        billion_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(tỷ|tỉ)', price_text)
        if billion_match:
            billion_part = extract_number(billion_match.group(1))
        
        # Tìm phần triệu
        million_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(triệu|tr)', price_text)
        if million_match:
            million_part = extract_number(million_match.group(1))
        
        if billion_part is not None or million_part is not None:
            total = (billion_part * 1000000000 if billion_part else 0) + \
                   (million_part * 1000000 if million_part else 0)
            return int(total)  # Trả về số nguyên
    
    # Xử lý định dạng chỉ có triệu
    elif 'triệu' in price_text or 'tr' in price_text:
        number = extract_number(price_text)
        return int(number * 1000000) if number else None  # Trả về số nguyên
    
    # Xử lý định dạng chỉ có nghìn
    elif 'nghìn' in price_text or 'k' in price_text:
        number = extract_number(price_text)
        return int(number * 1000) if number else None  # Trả về số nguyên
    
    else:
        # Nếu không có đơn vị rõ ràng, thử trích xuất số và đoán đơn vị
        number = extract_number(price_text)
        if number:
            # Nếu số lớn hơn 1000, giả sử là triệu
            if number > 1000:
                return int(number * 1000000)  # Trả về số nguyên
            else:
                return int(number * 1000000)  # Mặc định là triệu cho số nhỏ
    
    return None
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
    """Trích xuất số km từ chuỗi văn bản - Sửa để xử lý đúng định dạng"""
    if not km_text or km_text == 'N/A':
        return None
        
    # Chuẩn hóa chuỗi km
    km_text = str(km_text).lower().replace('km', '').strip()
    
    # Xử lý trường hợp có dấu chấm phân cách hàng nghìn (ví dụ: 3.900 km)
    if '.' in km_text and len(km_text.split('.')[-1]) == 3:
        # Đây có thể là dấu chấm phân cách hàng nghìn
        km_text = km_text.replace('.', '')
    
    # Trích xuất số
    number = extract_number(km_text)
    return number

def format_km(km_value):
    """Định dạng số km thành chuỗi dễ đọc - Sửa để hiển thị đúng số km"""
    if not km_value:
        return "N/A"
    
    # Nếu km_value là số thập phân (ví dụ: 3.9) nhưng thực tế là 3900 km
    if km_value < 100:  # Giả sử nếu giá trị nhỏ hơn 100, có thể là đang bị hiểu nhầm thành nghìn km
        # Kiểm tra xem có phải là số thập phân không (ví dụ: 3.9 thực tế là 3900 km)
        if isinstance(km_value, float) and km_value != int(km_value):
            # Nhân với 1000 để chuyển thành km thực tế
            km_value = km_value * 1000
    
    # Định dạng số với dấu phân cách hàng nghìn
    if km_value >= 1000000:
        return f"{km_value / 1000000:.1f} triệu km".replace('.', ',')
    elif km_value >= 1000:
        # Hiển thị đầy đủ số km với dấu phân cách
        formatted_km = f"{km_value:,.0f}".replace(',', '.')
        return f"{formatted_km} km"
    else:
        return f"{int(km_value)} km"

def extract_year(year_text):
    """Trích xuất năm từ chuỗi văn bản"""
    if not year_text or year_text == 'N/A':
        return None
    
    # Loại bỏ các từ không cần thiết
    year_text = str(year_text).replace('Năm SX:', '').strip()
    
    # Tìm số có 4 chữ số (năm)
    matches = re.findall(r'\b(19|20)\d{2}\b', str(year_text))
    if matches:
        return int(matches[0] + year_text[-2:])  # Ghép lại để lấy năm đầy đủ
    
    # Nếu không tìm thấy theo cách trên, thử trích xuất số trực tiếp
    number = extract_number(year_text)
    if number and 1900 <= number <= 2030:
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
    """Chuẩn hóa dữ liệu xe - phiên bản đơn giản chỉ giữ giá trị số"""
    normalized = car_data.copy()
    
    # Chuẩn hóa từng trường
    if 'title' in normalized:
        normalized['title'] = clean_car_name(normalized['title'])
    
    # Price đã là số, không cần xử lý thêm
    # Chỉ cần đảm bảo price là số nguyên nếu có
    if 'price' in normalized and normalized['price'] is not None:
        normalized['price'] = int(normalized['price'])
    
    if 'km_driven' in normalized and normalized['km_driven'] != 'N/A':
        km_value = extract_km(normalized['km_driven'])
        if km_value:
            normalized['km_driven'] = int(km_value)
    
    if 'manufacture_year' in normalized and normalized['manufacture_year'] != 'N/A':
        year_value = extract_year(normalized['manufacture_year'])
        if year_value:
            normalized['manufacture_year'] = year_value
    
    # Chuẩn hóa các trường text khác
    text_fields = ['fuel', 'transmission', 'condition', 'origin', 'location']
    for field in text_fields:
        if field in normalized and normalized[field] != 'N/A':
            if field == 'fuel':
                normalized[field] = extract_fuel_type(normalized[field])
            elif field == 'transmission':
                normalized[field] = extract_transmission(normalized[field])
            elif field == 'condition':
                normalized[field] = extract_car_condition(normalized[field])
            elif field == 'origin':
                normalized[field] = extract_origin(normalized[field])
            elif field == 'location':
                normalized[field] = clean_location(normalized[field])
    
    if 'description' in normalized and normalized['description'] != 'N/A':
        normalized['description'] = clean_text(normalized['description'])
    
    # Xóa các trường không cần thiết nếu có
    fields_to_remove = ['price_raw', 'price_display', 'price_value', 'km_value', 'km_display']
    for field in fields_to_remove:
        if field in normalized:
            del normalized[field]
    
    return normalized