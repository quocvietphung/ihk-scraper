from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Hàm lấy thông tin chi tiết công việc
def scrape_job_details(driver):
    try:
        job_details_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.flex.flex-col.lg\\:p-8'))
        )
        job_details = job_details_container.text
        print("Job Details:", job_details)
    except Exception as e:
        print(f"Error scraping job details: {e}")


# Hàm click vào từng phần tử công việc
def click_job_offer(driver):
    job_offers = driver.find_elements(By.CSS_SELECTOR, 'a[data-turbo="true"]')
    for job in job_offers:
        try:
            # Cuộn đến phần tử trước khi click
            driver.execute_script("arguments[0].scrollIntoView(true);", job)
            time.sleep(1)  # Đợi một chút để đảm bảo phần tử đã cuộn vào khung nhìn
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(job)).click()  # Đợi phần tử có thể click được và click
            time.sleep(2)  # Đợi phần chi tiết tải
            scrape_job_details(driver)  # Lấy chi tiết công việc
        except Exception as e:
            print(f"Error clicking job offer: {e}")


# Hàm cuộn xuống và click vào nút "Next Page"
def click_next_page(driver):
    try:
        next_page_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/main/div[1]/div/div[1]/div/div[4]/div[1]/nav/a[@rel="next"]'))
        )
        # Cuộn xuống để đảm bảo nút nằm trong viewport
        driver.execute_script("arguments[0].scrollIntoView(true);", next_page_button)
        time.sleep(1)
        next_page_button.click()  # Click vào nút "Next Page"
        time.sleep(3)  # Đợi trang tải
        return True
    except Exception as e:
        print(f"Error clicking next page: {e}")
        return False


# Hàm duyệt và chuyển trang liên tục
def scrape_all_pages(driver):
    while True:
        # Duyệt các công việc trong trang hiện tại
        click_job_offer(driver)

        # Sau khi duyệt xong, click vào nút "Next Page" nếu có, nếu không thì dừng lại
        if not click_next_page(driver):
            break


# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Mở trang web
driver.get("https://www.azubi.de/beruf/ausbildung-pflegefachfrau/ausbildungsplaetze")

# Duyệt qua tất cả các trang và lấy chi tiết công việc
scrape_all_pages(driver)

# Đóng trình duyệt
driver.quit()
