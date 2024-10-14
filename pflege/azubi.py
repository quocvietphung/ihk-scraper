from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import pandas as pd


# Hàm cuộn xuống tới phần tử phân trang
def scroll_to_pagination(driver):
    pagination_bottom = driver.find_element(By.CLASS_NAME, "pagination-sorting-bottom")
    driver.execute_script("arguments[0].scrollIntoView();", pagination_bottom)
    time.sleep(2)


# Hàm kiểm tra và nhấn vào nút chuyển trang bằng JavaScript
def next_page_exists(driver):
    try:
        next_button = driver.find_element(By.XPATH, '//a[contains(@href, "page=") and contains(., "›")]')
        driver.execute_script("arguments[0].scrollIntoView();", next_button)
        driver.execute_script("arguments[0].click();", next_button)
        return True
    except NoSuchElementException:
        return False


# Hàm kiểm tra và nhấn vào nút "ERLAUBEN" nếu popup xuất hiện
def allow_push_notifications(driver):
    try:
        allow_button = driver.find_element(By.XPATH, '//button[contains(text(), "ERLAUBEN")]')
        allow_button.click()
        print("Đã nhấn vào 'ERLAUBEN'.")
    except NoSuchElementException:
        print("Không có pop-up 'ERLAUBEN'.")


# Hàm lấy thông tin từ thẻ <div class="card-body"> có chứa thông tin liên hệ
def get_contact_details(driver):
    data = {}
    try:
        card_bodies = driver.find_elements(By.CLASS_NAME, 'card-body')
        for card_body in card_bodies:
            if "Kontakt für Bewerber" in card_body.text:
                # Lấy thông tin liên hệ
                data['name'] = card_body.find_element(By.XPATH,
                                                      './/div[contains(@class, "contact-value")]/p').text.strip()
                data['branche'] = card_body.find_element(By.XPATH,
                                                         './/div[contains(text(), "Branche")]/following-sibling::div').text.strip()
                email_elements = card_body.find_elements(By.XPATH, './/a[contains(@href, "mailto:")]')
                data['email'] = email_elements[0].get_attribute('href').replace("mailto:",
                                                                                "") if email_elements else None
                telefon_elements = card_body.find_elements(By.XPATH, './/a[contains(text(), "Telefonnummer anzeigen")]')
                data['telefon'] = telefon_elements[0].text if telefon_elements else "Telefonnummer anzeigen"
                website_elements = card_body.find_elements(By.XPATH, './/div[contains(@class, "website")]/a')
                data['url'] = website_elements[0].get_attribute('href') if website_elements else None
                return data  # Trả về dữ liệu liên hệ đầu tiên tìm thấy

    except NoSuchElementException:
        print("Không tìm thấy thẻ <div class='card-body'> với thông tin liên hệ.")

    return data


# Hàm duyệt qua các trang và lấy chi tiết công việc
def scrape_all_pages(driver):
    while True:
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ci-search-result")))

            allow_push_notifications(driver)
            scroll_to_pagination(driver)

            jobs = driver.find_elements(By.CLASS_NAME, "ci-search-result")

            for job in jobs:
                job_title = job.find_element(By.CLASS_NAME, "vacancy__title").text
                job_location = job.find_element(By.CLASS_NAME, "vacancy__location").text
                job_url = job.find_element(By.CLASS_NAME, "vacancy__link").get_attribute("href")
                print(f"Job Title: {job_title}, Location: {job_location}, URL: {job_url}")

                driver.get(job_url)
                time.sleep(2)  # Chờ trang tải

                # Lấy thông tin từ thẻ <div class="card-body"> chứa thông tin liên hệ
                contact_data = get_contact_details(driver)
                if contact_data:
                    # Kết hợp thông tin việc làm với thông tin liên hệ
                    contact_data["job_title"] = job_title
                    contact_data["job_location"] = job_location
                    contact_data["job_url"] = job_url

                    # Lưu dữ liệu vào file CSV ngay sau khi thu thập
                    df = pd.DataFrame([contact_data])  # Đưa vào DataFrame với một hàng
                    df.to_csv("job_contact_details.csv", mode='a', index=False,
                              header=not bool(pd.read_csv("job_contact_details.csv").shape[0]))
                    print("Đã lưu dữ liệu vào file job_contact_details.csv.")

                driver.back()
                time.sleep(2)

            if not next_page_exists(driver):
                print("Đã duyệt qua tất cả các trang.")
                break

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
