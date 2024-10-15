from selenium import webdriver
from selenium.webdriver.common.by import By

# Khởi động trình duyệt
driver = webdriver.Chrome()

# Mở trang web mục tiêu
url = 'https://jobs.ausbildungsheld.de/stellenangebot/ausbildung-zur-m-staatlich-geprueften-pflegefachfrau-pflegefachmann-BS3MY9'
driver.get(url)

# Khởi tạo dictionary để lưu trữ thông tin
job_data = {
    'Name': '',
    'Branche': '',
    'Email': '',
    'Telefon': '',
    'Website': ''
}

# Lấy thông tin Name từ thẻ chứa tên công ty
try:
    name_element = driver.find_element(By.CSS_SELECTOR, 'div.contact-label')
    job_data['Name'] = name_element.text
except Exception as e:
    print(f"Error getting Name: {e}")

# Lấy thông tin Branche từ thẻ chứa ngành nghề
try:
    branche_element = driver.find_element(By.CSS_SELECTOR, 'div.contact-value a[href*="/branche/"]')
    job_data['Branche'] = branche_element.text
except Exception as e:
    print(f"Error getting Branche: {e}")

# Lấy thông tin Email từ thẻ a chứa mailto:
try:
    email_element = driver.find_element(By.CSS_SELECTOR, 'a[href^="mailto:"]')
    job_data['Email'] = email_element.text
except Exception as e:
    print(f"Error getting Email: {e}")

# Lấy thông tin Telefon từ thẻ chứa số điện thoại (thay thế logic)
try:
    telefon_element = driver.find_element(By.CSS_SELECTOR, "span.content-swap a[href^='tel:']")
    job_data['Telefon'] = telefon_element.get_attribute('href').replace('tel:', '')
except Exception as e:
    print(f"Error getting Telefon: {e}")

# Lấy thông tin Website từ thẻ chứa link trang web
try:
    website_element = driver.find_element(By.CSS_SELECTOR, 'div.website a')
    job_data['Website'] = website_element.get_attribute('href')
except Exception as e:
    print(f"Error getting Website: {e}")

# In ra thông tin đã thu thập được
print(job_data)

# Đóng trình duyệt
driver.quit()
