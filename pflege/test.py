from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re

# Hàm lấy email từ trang web
def scrape_email(driver, company_url):
    try:
        driver.get(company_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Tìm tất cả các thẻ <a> có chứa email (href="mailto:...")
        mailto_links = driver.find_elements(By.CSS_SELECTOR, 'a[href^="mailto:"]')
        emails = [link.get_attribute('href').replace('mailto:', '') for link in mailto_links]

        # Nếu không tìm thấy email với mailto, tìm kiếm email trong văn bản trang
        if not emails:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            # Sử dụng regex để tìm email trong văn bản trang
            emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", page_text)

        if emails:
            print(f"Emails found on {company_url}: {emails}")
        else:
            print(f"No email found on {company_url}")
    except Exception as e:
        print(f"Error retrieving email from {company_url}: {e}")

# Khởi tạo trình duyệt
driver = webdriver.Chrome()

# Danh sách các công ty và URL của họ (cần cập nhật với các trang thực tế)
companies = {
    "Vivantes": "https://www.vivantes.de/",
    "Charité": "https://www.charite.de/",
    "Helios Kliniken": "https://www.helios-gesundheit.de/",
    "St. Augustinus Gruppe": "https://www.st-augustinus-kliniken.de/",
    "VIDACTA Schulen": "https://www.vidacta.de/",
    "ProCurand": "https://www.procurand.de/",
    "CBT Caritas": "https://www.cbt-gmbh.de/",
    "ESO Education Group": "https://www.eso.de/",
    "Justiz des Landes Nordrhein-Westfalen": "https://www.justiz.nrw.de/"
}

# Lấy email cho từng công ty
for company, url in companies.items():
    scrape_email(driver, url)

# Đóng trình duyệt sau khi hoàn thành
driver.quit()
