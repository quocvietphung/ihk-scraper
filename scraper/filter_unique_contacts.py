import pandas as pd

# Đường dẫn đến file CSV của bạn
file_path = 'ihk_jobs.csv'  # Đường dẫn đến file CSV của bạn

# Đọc file CSV với encoding và separator phù hợp
try:
    # Sử dụng mã hóa utf-8 để đảm bảo đọc chính xác các ký tự đặc biệt
    df = pd.read_csv(file_path, sep=';', encoding='utf-8', on_bad_lines='skip')

    # Loại bỏ các dòng trùng lặp dựa trên 'Email' và 'Unternehmen'
    df_cleaned = df.drop_duplicates(subset=['Email', 'Unternehmen'], keep='first')

    # Loại bỏ các dòng có giá trị NaN ở cả 'Email' và 'Unternehmen'
    df_cleaned = df_cleaned.dropna(subset=['Email', 'Unternehmen'])

    # Lọc dữ liệu theo các ngành: Koch/Köchin, Kaufmann/-frau, và Hotelfachmann/-frau
    filtered_df = df_cleaned[df_cleaned['Branche'].str.contains('Koch/Köchin|Kaufmann/-frau|Hotelfachmann/-frau', case=False, na=False)]

    # Chọn các cột cần thiết và đưa "Unternehmen" sau "Nachname"
    result_df = filtered_df[['Anrede', 'Vorname', 'Nachname', 'Unternehmen', 'Branche', 'Telefonnumer', 'Email']]

    # Hiển thị vài dòng đầu tiên của dữ liệu đã lọc
    print(result_df.head())

    # Lưu dữ liệu đã lọc ra file CSV mới với mã hóa utf-8
    output_file_path = 'filtered_unique_kontakt.csv'
    result_df.to_csv(output_file_path, index=False, encoding='utf-8')

    print(f"File đã được lưu tại: {output_file_path}")

except Exception as e:
    print(f"Lỗi khi đọc file: {e}")