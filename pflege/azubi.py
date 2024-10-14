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

# Hàm kiểm tra và nhấn vào nút chuyển trang bằng JavaScript
def next_page_exists(driver):
    try:
        # Tìm nút chứa ký tự '›' để chuyển trang
        next_button = driver.find_element(By.XPATH, '//a[contains(@href, "page=") and contains(., "›")]')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)  # Cuộn tới nút
        driver.execute_script("arguments[0].click();", next_button)  # Nhấn vào nút bằng JavaScript
        return True
    except NoSuchElementException:
        return False

# Hàm kiểm tra và nhấn vào nút "ERLAUBEN" nếu popup xuất hiện
def allow_push_notifications(driver):
    try:
        # Tìm nút "ERLAUBEN" nếu popup xuất hiện
        allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "ERLAUBEN")]')
        allow_button.click()  # Nhấn vào nút "ERLAUBEN"
        print("Đã nhấn vào 'ERLAUBEN'.")
    except NoSuchElementException:
        print("Không có pop-up 'ERLAUBEN'.")

# Hàm duyệt qua các trang và lấy chi tiết công việc
def scrape_all_pages(driver):
    while True:
        try:
            # Chờ các mục công việc xuất hiện
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ci-search-result")))

            # Kiểm tra và nhấn vào "ERLAUBEN" nếu popup xuất hiện
            allow_push_notifications(driver)

            # Cuộn xuống tới phần phân trang
            scroll_to_pagination(driver)

            # Lấy danh sách các công việc
            jobs = driver.find_elements(By.CLASS_NAME, "ci-search-result")

            # In thông tin các công việc
            for job in jobs:
                job_title = job.find_element(By.CLASS_NAME, "vacancy__title").text
                job_location = job.find_element(By.CLASS_NAME, "vacancy__location").text
                job_url = job.find_element(By.CLASS_NAME, "vacancy__link").get_attribute("href")
                print(f"Job Title: {job_title}, Location: {job_location}, URL: {job_url}")

            # Tìm và nhấn nút chuyển trang
            if not next_page_exists(driver):
                print("Đã duyệt qua tất cả các trang.")
                break

        except TimeoutException:
            print("Timeout khi chờ các phần tử công việc tải.")
            break

# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Mở trang web
driver.get("https://jobs.ausbildungsheld.de/suchergebnisse?q=Ausbildung+Pflegefach&l=&r=25km&_multiselect_r=25km&a=&s=relevance&da=")

# Duyệt qua tất cả các trang và lấy chi tiết công việc
scrape_all_pages(driver)

# Đóng trình duyệt
driver.quit()
