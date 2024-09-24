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

    # Lưu 5 dòng đầu tiên vào file CSV mới
    output_file_5rows = 'first_5_rows_filtered_unique_kontakt.csv'
    result.to_csv(output_file_5rows, index=False, encoding='utf-8')

    print(f"File chứa 5 dòng đầu tiên đã được lưu tại: {output_file_5rows}")

except Exception as e:
    print(f"Lỗi khi đọc file: {e}")
