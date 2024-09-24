from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_address(url):
    # Cài đặt và sử dụng ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Mở trang web
    driver.get(url)

    # Đợi trang tải xong
    wait = WebDriverWait(driver, 10)

    try:
        # Tìm khối chứa thông tin liên hệ
        contact_container = wait.until(EC.visibility_of_element_located((By.ID, 'contact_container')))

        # Lấy toàn bộ văn bản trong contact_container
        contact_text = contact_container.text

        print("Contact text:", contact_text)

        # Tách các dòng và trích xuất thông tin địa chỉ
        lines = contact_text.split('\n')

        # Thông tin công ty và địa chỉ
        company_name = lines[2]  # Pullman Munich
        street_address = lines[3]  # Theodor-Dombart-Straße 4
        postal_code_city = lines[4]  # 80805 München

        # Kết hợp các thành phần địa chỉ
        address = f"{company_name}, {street_address}, {postal_code_city}"

        # In ra địa chỉ
        print("Address:", address)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Đóng trình duyệt sau khi hoàn tất
        driver.quit()

if __name__ == '__main__':
    # URL của trang chi tiết công việc
    url = 'https://www.hotelcareer.de/jobs/pullman-munich-27789/auszubildende-hotelfachmann-hotelfachfrau-m-w-d-2794249?rltr=dyn'

    # Gọi hàm để lấy địa chỉ
    scrape_address(url)
