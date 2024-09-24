from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

def close_popups(driver, wait):
    """Hàm đóng các popup cookie và popup khác trên trang."""
    try:
        # Tìm và nhấp vào nút đồng ý cookie (nếu có)
        accept_cookies_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Zustimmen' or text()='Accept' or text()='I agree']")))
        accept_cookies_button.click()
        print("Cookie popup closed.")
    except:
        print("No cookie popup found or unable to close cookie popup.")

    try:
        # Đóng các popup khác, ví dụ popup quảng cáo, đăng ký, v.v.
        close_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@class='close' or @aria-label='Close']")))
        close_button.click()
        print("Other popup closed.")
    except:
        print("No other popup found or unable to close other popup.")

def get_contact_info(driver):
    """Hàm lấy thông tin liên hệ từ trang chi tiết công việc."""
    try:
        # Sử dụng WebDriverWait để chờ phần tử contact_container xuất hiện
        wait = WebDriverWait(driver, 10)
        contact_container = wait.until(EC.visibility_of_element_located((By.ID, 'contact_container')))

        # Lấy thông tin liên hệ, nếu không tìm thấy sẽ gán giá trị "N/A"
        try:
            contact_name = contact_container.find_element(By.XPATH, "//span[@class='contact_name']").text
        except:
            contact_name = "N/A"

        try:
            contact_position = contact_container.find_element(By.XPATH, "//span[@class='contact_position']").text
        except:
            contact_position = "N/A"

        # Tìm số điện thoại trong <div id='contact_fields'>
        try:
            contact_fields = contact_container.find_element(By.ID, 'contact_fields').get_attribute('innerHTML')
            # Tìm nội dung văn bản chứa số điện thoại bắt đầu bằng +49
            phone_number = [line for line in contact_fields.split('<br>') if '+49' in line][0].strip()
        except:
            phone_number = "N/A"

        # Lấy email
        try:
            email = contact_container.find_element(By.XPATH, "//a[contains(@href, 'mailto:')]").get_attribute('href')
            email = email.replace("mailto:", "")  # Loại bỏ 'mailto:'
        except:
            email = "N/A"

        # Lấy chính xác website
        try:
            website = contact_container.find_element(By.XPATH, "//a[contains(@href, 'http')]").get_attribute('href')
        except:
            website = "N/A"

        # Xử lý chuỗi văn bản để lấy địa chỉ
        try:
            address_lines = contact_container.text.split('\n')
            street_address = address_lines[3]
            postal_code_city = address_lines[4]
            address = f"{street_address}, {postal_code_city}"
        except:
            address = "N/A"

        # Tách Anrede và tên riêng
        anrede = ""
        name = contact_name
        if 'Frau' in contact_name:
            anrede = 'Frau'
            name = contact_name.replace('Frau', '').strip()
        elif 'Herr' in contact_name:
            anrede = 'Herr'
            name = contact_name.replace('Herr', '').strip()

    except Exception as e:
        print(f"Error extracting contact info: {e}")
        anrede, name, phone_number, email, website, address = "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"

    return anrede, name, phone_number, email, website, address

def get_job_listings(url, output_file):
    # Sử dụng webdriver-manager để cài đặt và sử dụng ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Mở trang web
    driver.get(url)

    # Đợi cho đến khi hộp tìm kiếm xuất hiện và sẵn sàng
    wait = WebDriverWait(driver, 10)

    # Đóng popup cookie và các popup khác (nếu có)
    close_popups(driver, wait)

    # Nhập từ khóa "Auszubildende/r Hotelfachmann/frau"
    search_box_keyword = wait.until(EC.element_to_be_clickable((By.ID, 'taetigkeiten')))
    search_box_keyword.clear()
    search_box_keyword.send_keys('Auszubildende/r Hotelfachmann/frau')

    # Nhập vị trí "Deutschland"
    search_box_location = wait.until(EC.element_to_be_clickable((By.ID, 'input_ort')))
    search_box_location.clear()
    search_box_location.send_keys('Deutschland')

    # Nhấn nút tìm kiếm
    search_button = wait.until(EC.element_to_be_clickable((By.ID, 'btnSearch_new')))
    search_button.click()

    time.sleep(5)  # Đợi một lúc để trang tải xong

    all_jobs = []

    while True:  # Lặp qua tất cả các trang
        # Lấy danh sách công việc
        job_listings = driver.find_elements(By.CLASS_NAME, 'result_list_right')

        # Duyệt qua các công việc và mở URL công việc chi tiết
        for job in job_listings:
            title = job.find_element(By.CLASS_NAME, 'job').text
            location = job.find_element(By.CLASS_NAME, 'location').text

            # Mở URL chi tiết của công việc
            job_link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
            print(f"Opening job link: {job_link}")
            driver.execute_script("window.open(arguments[0]);", job_link)
            driver.switch_to.window(driver.window_handles[1])

            # Đợi trang công việc tải, giới hạn 16 giây
            try:
                WebDriverWait(driver, 16).until(
                    EC.presence_of_element_located((By.ID, 'contact_container')))
            except:
                print(f"Timed out waiting for page to load: {job_link}")

            # Lấy thông tin liên hệ từ trang chi tiết công việc
            anrede, name, phone_number, email, website, address = get_contact_info(driver)

            # Lưu thông tin vào danh sách
            all_jobs.append([title, location, anrede, name, phone_number, email, website, address])

            # Đóng tab hiện tại và quay về tab chính
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        # Kiểm tra xem có trang tiếp theo không
        try:
            next_page_button = driver.find_element(By.CLASS_NAME, 'weiter')
            next_page_button.click()
            time.sleep(5)  # Đợi trang tiếp theo tải
        except:
            print("No more pages found.")
            break

    # Đóng trình duyệt sau khi hoàn tất
    driver.quit()

    # Lưu vào CSV với mã hóa UTF-8
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Cập nhật tiêu đề các cột bằng tiếng Đức
        writer.writerow(["Berufsbezeichnung", "Ort", "Anrede", "Name", "Telefonnummer", "E-Mail", "Webseite", "Adresse"])
        for job in all_jobs:
            writer.writerow(job)

    print(f"{len(all_jobs)} job listings have been saved to {output_file}")

if __name__ == '__main__':
    # URL của trang
    url = 'https://www.hotelcareer.de/jobs/stellenangebote'
    output_file = 'job_listings.csv'

    # Gọi hàm để lấy danh sách công việc và lưu vào CSV
    get_job_listings(url, output_file)
