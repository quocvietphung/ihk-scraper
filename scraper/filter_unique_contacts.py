import pandas as pd


# Hàm định dạng số điện thoại: thay thế mã +49 bằng số 0
def format_phone_number(phone):
    """Định dạng lại số điện thoại, thay thế mã quốc gia +49 bằng số 0."""
    digits_only = ''.join(filter(lambda x: x.isdigit() or x == '+', str(phone)))

    # Nếu số bắt đầu bằng +49, thay thế bằng 0
    if digits_only.startswith('+49'):
        digits_only = '0' + digits_only[3:]

    return digits_only if len(digits_only) >= 7 else ""


# Hàm làm sạch định dạng số điện thoại
def clean_phone_format(phone):
    """Xóa các ký tự đặc biệt và định dạng lại số điện thoại."""
    if isinstance(phone, str):  # Kiểm tra nếu phone là chuỗi
        cleaned_phone = phone.replace('-', '').replace('/', '').replace(' ', '')
        return format_phone_number(cleaned_phone)
    else:
        return ""  # Nếu không phải chuỗi, trả về chuỗi rỗng


# Đọc file CSV vào dataframe
file_path = 'ihk_jobs.csv'  # Thay bằng đường dẫn tới file của bạn

# Đọc file với dấu phân cách là dấu chấm phẩy
try:
    df = pd.read_csv(file_path, sep=';', on_bad_lines='skip')  # Sử dụng 'sep=";"' để xử lý dấu phân cách
except Exception as e:
    print(f"Lỗi khi đọc file: {e}")

# Kiểm tra tên các cột trong file CSV để đảm bảo tên cột chính xác
print("Tên các cột trong file CSV:", df.columns)

# Làm sạch định dạng cột 'Telefon'
if 'Telefon' in df.columns:
    df['Telefon'] = df['Telefon'].apply(clean_phone_format)

# Lọc bỏ các dòng trùng lặp dựa trên cột 'Email' hoặc 'email', giữ lại lần xuất hiện đầu tiên
df_cleaned = df.drop_duplicates(subset=['Email'])  # Thay 'Email' bằng tên cột chính xác nếu khác

# Lọc ra các cột cần thiết: 'Vorname', 'Nachname', 'Telefon', 'Email'
result_df = df_cleaned[['Vorname', 'Nachname', 'Telefon', 'Email']]  # Đảm bảo tên cột phù hợp

# Lưu dữ liệu đã lọc ra file CSV mới
output_file_path = 'unique.csv'  # Thay bằng đường dẫn bạn muốn lưu file
result_df.to_csv(output_file_path, index=False)

print(f"File đã được lưu tại: {output_file_path}")
