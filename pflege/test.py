from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Khởi tạo trình duyệt (ở đây sử dụng Chrome)
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Chạy trong chế độ headless (không hiển thị trình duyệt)
driver = webdriver.Chrome(options=options)

# Truy cập vào URL
url = 'https://jobs.ausbildungsheld.de/stellenangebot/ausbildung-zur-pflegefachfrau-zum-pflegefachmann-m-w-d-in-ingolstadt-9KF7MJ'
driver.get(url)

# Đợi một thời gian ngắn để đảm bảo trang đã tải đầy đủ
time.sleep(2)

# Tìm thẻ <div class="contact-value"> chứa thông tin liên hệ
try:
    contact_section = driver.find_element(By.CSS_SELECTOR, "div.contact-value")

    # Lấy thông tin địa chỉ
    try:
        street_address = contact_section.find_element(By.CSS_SELECTOR, "div.street-address").text
        postal_code = contact_section.find_element(By.CSS_SELECTOR, "span.postal-code").text
        locality = contact_section.find_element(By.CSS_SELECTOR, "span.locality").text
        country_name = contact_section.find_element(By.CSS_SELECTOR, "div.country-name").text
        print("Địa chỉ:", f"{street_address}, {postal_code} {locality}, {country_name}")
    except:
        print("Không tìm thấy thông tin địa chỉ")

    # Lấy thông tin website
    try:
        website = contact_section.find_element(By.CSS_SELECTOR, "div.website a").get_attribute("href")
        print("Website:", website)
    except:
        print("Không tìm thấy thông tin Website")

    # Lấy thông tin số điện thoại
    try:
        phone = contact_section.find_element(By.CSS_SELECTOR, "span.cs-content a").text
        print("Số điện thoại:", phone)
    except:
        print("Không tìm thấy thông tin Số điện thoại")

    # Lấy thông tin email
    try:
        email = contact_section.find_element(By.CSS_SELECTOR, "div.email a").get_attribute("href")
        email = email.replace("mailto:", "")  # Loại bỏ phần 'mailto:'
        print("Email:", email)
    except:
        print("Không tìm thấy thông tin Email")

except Exception as e:
    print("Không tìm thấy phần tử thẻ 'contact-value':", e)

# Đóng trình duyệt sau khi thực thi xong
driver.quit()
