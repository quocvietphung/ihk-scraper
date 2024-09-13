import pandas as pd

# Đường dẫn đến file CSV mà bạn đã lưu
output_file_path = 'filtered_unique_kontakt.csv'

# Đọc file CSV
try:
    df_output = pd.read_csv(output_file_path, encoding='utf-8')

    # Lấy 5 dòng đầu tiên
    result = df_output.head(5)

    # Hiển thị 5 dòng đầu tiên
    print(result)

except Exception as e:
    print(f"Lỗi khi đọc file: {e}")
