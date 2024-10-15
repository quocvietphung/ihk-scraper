from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time


# Hàm cuộn xuống tới phần tử phân trang
def scroll_to_pagination(driver):
    pagination_bottom = driver.find_element(By.CLASS_NAME, "pagination-sorting-bottom")
    driver.execute_script("arguments[0].scrollIntoView();", pagination_bottom)
    time.sleep(2)


# Hàm kiểm tra và nhấn vào nút chuyển trang bằng JavaScript, đồng thời in ra số trang
def next_page_exists(driver, current_page):
    try:
        next_button = driver.find_element(By.XPATH, '//a[contains(@href, "page=") and contains(., "›")]')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        print(f"Chuyển sang trang {current_page + 1}")
        return True
    except NoSuchElementException:
        return False


# Hàm lấy thông tin liên hệ từ trang chi tiết công việc
def get_contact_info(url):
    # Khởi động trình duyệt
    driver = webdriver.Chrome()

    # Mở trang web mục tiêu
    driver.get(url)

    # Khởi tạo dictionary để lưu trữ thông tin
    job_data = {
        'Name': 'N/A',  # Giá trị mặc định là "N/A"
        'Company': 'N/A',
        'Branche': 'N/A',
        'Email': 'N/A',
        'Telefon': 'N/A',
        'Website': 'N/A'
    }

    # Lấy thông tin Name từ vị trí XPath đầu tiên
    try:
        name_element_1 = driver.find_element(By.XPATH,
                                             '/html/body/div[1]/div[3]/div/div[4]/div[1]/div[2]/div/div[2]/div/div[2]/div/div[2]/p')
        name_text = name_element_1.get_attribute('innerHTML')
        job_data['Name'] = name_text.split('<br>')[0].strip() if name_text else "N/A"
    except NoSuchElementException:
        job_data['Name'] = "N/A"  # Đặt về "N/A" nếu không tìm thấy

    # Lấy thông tin Company từ thẻ chứa tên công ty
    try:
        company_element = driver.find_element(By.CSS_SELECTOR, 'div.contact-label')
        job_data['Company'] = company_element.text.strip()
    except NoSuchElementException:
        job_data['Company'] = "N/A"

    # Lấy thông tin Branche từ thẻ <h1> với lớp cụ thể
    try:
        branche_element = driver.find_element(By.CSS_SELECTOR, 'h1.page-title.th-page-title.js-page-title')
        job_data['Branche'] = branche_element.text.strip()  # Lấy nội dung văn bản từ thẻ <h1>
    except NoSuchElementException:
        job_data['Branche'] = "N/A"

    # Lấy thông tin Email từ thẻ a chứa mailto:
    try:
        email_element = driver.find_element(By.CSS_SELECTOR, 'div.email a[href^="mailto:"]')
        email_full = email_element.get_attribute('href').replace('mailto:', '')
        job_data['Email'] = email_full.split('?')[0] if email_full else "N/A"
    except NoSuchElementException:
        job_data['Email'] = "N/A"

    # Lấy thông tin Telefon từ thẻ chứa số điện thoại
    try:
        telefon_element = driver.find_element(By.CSS_SELECTOR, "span.content-swap a[href^='tel:']")
        job_data['Telefon'] = telefon_element.get_attribute('href').replace('tel:', '')
    except NoSuchElementException:
        job_data['Telefon'] = "N/A"

    # Lấy thông tin Website từ thẻ chứa link trang web
    try:
        website_element = driver.find_element(By.CSS_SELECTOR, 'div.website a')
        job_data['Website'] = website_element.get_attribute('href').strip()
    except NoSuchElementException:
        job_data['Website'] = "N/A"

    # In ra thông tin đã thu thập được
    print(job_data)

    # Đóng trình duyệt
    driver.quit()


# Hàm duyệt qua các trang và lấy chi tiết công việc
def scrape_all_pages(driver):
    current_page = 1
    print(f"Đang ở trang {current_page}")

    while True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ci-search-result")))

            scroll_to_pagination(driver)

            jobs = driver.find_elements(By.CLASS_NAME, "ci-search-result")

            for job in jobs:
                try:
                    job_title = job.find_element(By.CLASS_NAME, "vacancy__title").text
                    job_location = job.find_element(By.CLASS_NAME, "vacancy__location").text
                    job_url = job.find_element(By.CLASS_NAME, "vacancy__link").get_attribute("href")
                    print(f"Job Title: {job_title}, Location: {job_location}, URL: {job_url}")

                    # Gọi hàm get_contact_info để lấy thông tin liên hệ cho từng URL công việc
                    get_contact_info(job_url)

                except NoSuchElementException:
                    continue

            if not next_page_exists(driver, current_page):
                print("Đã duyệt qua tất cả các trang.")
                break

            current_page += 1

        except TimeoutException:
            print("Timeout khi chờ các phần tử công việc tải.")
            break


# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Mở trang web
driver.get(
    "https://jobs.ausbildungsheld.de/suchergebnisse?q=Ausbildung+Pflegefach&l=&r=25km&_multiselect_r=25km&a=&s=relevance&da=")

# Duyệt qua tất cả các trang và lấy chi tiết công việc
scrape_all_pages(driver)

# Đóng trình duyệt
driver.quit()