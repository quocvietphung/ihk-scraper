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
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable(job)).click()  # Đợi phần tử có thể click được và click
            time.sleep(2)  # Đợi phần chi tiết tải
            scrape_job_details(driver)  # Lấy chi tiết công việc
        except Exception as e:
            print(f"Error clicking job offer: {e}")

# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Mở trang web
driver.get("https://www.azubi.de/suche?text=Ausbildung+Pflege")

# Click và lấy chi tiết công việc
click_job_offer(driver)

# Đóng trình duyệt
driver.quit()
