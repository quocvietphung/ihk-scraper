from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# Khởi tạo trình duyệt
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Truy cập trang web
driver.get(
    'https://www.pflegeausbildung.net/ausbildung/uebersicht-pflegeschulen.html?tx_bafzaaltenpflegeschulen_demap%5Baction%5D=list&tx_bafzaaltenpflegeschulen_demap%5Bcontroller%5D=Altenpflegeschule&cHash=8a87772c409ade57cb257ebe18c54abc')

# Sử dụng WebDriverWait để chờ cho trang tải đầy đủ
wait = WebDriverWait(driver, 20)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".paginationWrapper")))

# Tạo danh sách để lưu thông tin
school_data = []
current_page = 1


# Hàm thu thập thông tin từ các trường trên trang hiện tại
def scrape_current_page():
    schools_section = driver.find_elements(By.CLASS_NAME, "row.even") + driver.find_elements(By.CLASS_NAME, "row.odd")
    for school in schools_section:
        try:
            # Thu thập thông tin từ cấu trúc HTML
            name = school.find_element(By.CSS_SELECTOR, ".col-xs-12.col-sm-3.col-md-3 a").text
            address = school.find_element(By.CSS_SELECTOR, ".col-xs-12.col-sm-3.col-md-2 a").text
            phone = school.find_element(By.CSS_SELECTOR, ".col-xs-12.col-sm-2.col-md-2 a").text
            email = school.find_element(By.CSS_SELECTOR, ".col-xs-12.col-sm-2.col-md-3 a").text

            # Lưu thông tin vào danh sách
            school_data.append({
                'Tên': name,
                'Địa chỉ': address,
                'Điện thoại': phone,
                'Email': email
            })

        except Exception as e:
            print(f"Lỗi khi thu thập thông tin: {e}")
            continue

    # In ra dữ liệu thu thập được trên trang hiện tại
    for data in school_data:
        print(f"Tên: {data['Tên']}")
        print(f"Địa chỉ: {data['Địa chỉ']}")
        print(f"Điện thoại: {data['Điện thoại']}")
        print(f"Email: {data['Email']}")
        print("----------")

    # In tổng số phần tử đã duyệt và trang hiện tại
    print(f"Tổng số phần tử đã duyệt: {len(school_data)}")
    print(f"Kết thúc ở trang số: {current_page}")
    print("________________________________________")


# Lặp qua tất cả các trang và thu thập dữ liệu
while True:
    # Thu thập thông tin trên trang hiện tại
    scrape_current_page()

    try:
        # Tìm nút phân trang và nút "Next" bằng CSS Selector
        pagination_wrapper = driver.find_element(By.XPATH, '/html/body/main/div/div/div/div[2]/div/div[4]/div[3]')
        next_button = pagination_wrapper.find_element(By.CSS_SELECTOR, 'li.next a')

        # Cuộn xuống nút "Next"
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(2)  # Thời gian chờ để đảm bảo nút hiển thị đầy đủ
        # Nhấn vào nút "Next"
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)  # Chờ trang mới tải xong
        current_page += 1
    except Exception as e:
        # Nếu không tìm thấy nút "next", tức là đã tới trang cuối cùng
        print(f"Không thể tìm thấy nút Next: {e}")
        break

# In tổng số phần tử đã duyệt và trang cuối cùng
print(f"Tổng số phần tử đã duyệt: {len(school_data)}")
print(f"Kết thúc ở trang số: {current_page}")

# Đóng trình duyệt
driver.quit()