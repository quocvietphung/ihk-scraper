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

# Hàm duyệt qua các trang và lấy chi tiết công việc
def scrape_all_pages(driver):
    current_page = 1  # Khởi tạo trang hiện tại là trang 1
    print(f"Đang ở trang {current_page}")

    while True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ci-search-result")))

            scroll_to_pagination(driver)

            jobs = driver.find_elements(By.CLASS_NAME, "ci-search-result")

            for job in jobs:
                job_title = job.find_element(By.CLASS_NAME, "vacancy__title").text
                job_location = job.find_element(By.CLASS_NAME, "vacancy__location").text
                job_url = job.find_element(By.CLASS_NAME, "vacancy__link").get_attribute("href")
                print(f"Job Title: {job_title}, Location: {job_location}, URL: {job_url}")

            # Kiểm tra xem có trang tiếp theo không
            if not next_page_exists(driver, current_page):
                print("Đã duyệt qua tất cả các trang.")
                break

            current_page += 1  # Tăng số trang sau khi chuyển trang

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