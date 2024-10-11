import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Cấu hình Chrome để mở trình duyệt trực quan
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Tự động cài đặt và quản lý ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL bạn cần lấy dữ liệu
url = "https://www.ausbildung.de/suche/?form_main_search[what]=Pflegefachmann/-frau&form_main_search[radius]=1000"
driver.get(url)

# Đợi trang tải xong
time.sleep(5)

# Hàm cuộn xuống cuối trang
def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Đợi trang tải thêm dữ liệu

# Hàm nhấn nút "Weitere Ergebnisse laden" nếu nút xuất hiện
def click_load_more_button():
    try:
        load_more_button = driver.find_element(By.CSS_SELECTOR, 'div.js-load-more-search-results button')
        if load_more_button.is_displayed():
            load_more_button.click()
            time.sleep(3)  # Đợi dữ liệu tải xong sau khi nhấn nút
            return True
    except:
        return False
    return False

# Hàm lấy lại danh sách các phần tử
def get_job_links():
    return driver.find_elements(By.CSS_SELECTOR, 'a.job-posting-cluster-cards__link')

# Hàm cuộn trang và thu thập tất cả liên kết công việc
def collect_all_job_links():
    job_links = []
    previous_count = -1
    max_attempts = 5  # Số lần thử tối đa nếu không có phần tử mới
    attempts = 0

    while attempts < max_attempts:
        scroll_to_bottom()
        click_load_more_button()
        time.sleep(2)  # Đợi trang tải thêm dữ liệu
        current_job_links = get_job_links()
        if len(current_job_links) > len(job_links):
            job_links = current_job_links
            attempts = 0  # Đặt lại số lần thử nếu có phần tử mới
        else:
            attempts += 1  # Tăng số lần thử nếu không có phần tử mới
    # Lấy các href từ các phần tử
    job_urls = [link.get_attribute("href") for link in job_links]
    return job_urls

# Tạo tệp CSV và mở chế độ ghi
with open('pflegefachmann.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Branche', 'Website', 'Anrede', 'Name', 'Telefonnummer', 'E-Mail'])  # Viết tiêu đề cột

    # Lấy tất cả các liên kết công việc sau khi cuộn xuống
    job_urls = collect_all_job_links()

    # Lặp qua từng công việc và mở URL
    for index, job_url in enumerate(job_urls):
        print(f"Website {index + 1}: {job_url}")

        # Mở từng URL
        driver.get(job_url)

        # Đợi trang mới tải xong
        time.sleep(3)

        # Lấy tiêu đề công việc
        try:
            job_title = driver.find_element(By.CSS_SELECTOR, 'h1').text
        except:
            job_title = "N/A"

        # Tìm thông tin liên hệ
        try:
            contact_name = driver.find_element(By.CSS_SELECTOR, '.job-posting-contact-person__name').text
        except:
            contact_name = "N/A"

        try:
            contact_position = driver.find_element(By.CSS_SELECTOR, '.job-posting-contact-person__position').text
        except:
            contact_position = "N/A"

        try:
            contact_email = driver.find_element(By.CSS_SELECTOR, '.job-posting-contact-person__email a').get_attribute('href').replace('mailto:', '')
        except:
            contact_email = "N/A"

        try:
            contact_phone = driver.find_element(By.CSS_SELECTOR, '.job-posting-contact-person__phone a').get_attribute('href').replace('tel:', '')
        except:
            contact_phone = "N/A"

        # Kiểm tra xem có "Frau" hoặc "Herr" trong phần Anrede
        if "Frau" in contact_name:
            anrede = "Frau"
        elif "Herr" in contact_name:
            anrede = "Herr"
        else:
            anrede = ""  # Nếu không có Anrede

        print(f"Branche: {job_title}, Anrede: {anrede}, Name: {contact_name}, Telefonnummer: {contact_phone}, E-Mail: {contact_email}")

        # Ghi dữ liệu vào tệp CSV
        writer.writerow([job_title, job_url, anrede, contact_name, contact_phone, contact_email])

# Đóng trình duyệt sau khi hoàn thành
driver.quit()

print("Đã lưu dữ liệu vào file pflegefachmann.csv")
