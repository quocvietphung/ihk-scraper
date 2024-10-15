from selenium import webdriver
from selenium.webdriver.common.by import By

def get_contact_info(url):
    # Khởi động trình duyệt
    driver = webdriver.Chrome()

    # Mở trang web mục tiêu
    driver.get(url)

    # Khởi tạo dictionary để lưu trữ thông tin
    job_data = {
        'Company': '',  # Đổi 'Name' thành 'Company'
        'Branche': '',
        'Email': '',
        'Telefon': '',
        'Website': ''
    }

    # Lấy thông tin Company từ thẻ chứa tên công ty
    try:
        company_element = driver.find_element(By.CSS_SELECTOR, 'div.contact-label')
        job_data['Company'] = company_element.text
    except Exception as e:
        print(f"Error getting Company: {e}")

    # Lấy thông tin Branche từ thẻ chứa ngành nghề
    try:
        branche_element = driver.find_element(By.CSS_SELECTOR, 'div.contact-value a[href*="/branche/"]')
        job_data['Branche'] = branche_element.text
    except Exception as e:
        print(f"Error getting Branche: {e}")

    # Lấy thông tin Email từ thẻ a chứa mailto:
    try:
        # Dùng CSS_SELECTOR đầu tiên
        email_element = driver.find_element(By.CSS_SELECTOR, 'div.email a[href^="mailto:"]')
        email_full = email_element.get_attribute('href').replace('mailto:', '')
        job_data['Email'] = email_full.split('?')[0]  # Chỉ lấy phần trước dấu '?'
    except Exception as e:
        print(f"Error getting Email with CSS_SELECTOR: {e}")
        # Thử dùng XPath khi CSS_SELECTOR thất bại
        try:
            email_element_xpath = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div[4]/div[1]/div[2]/div/div[2]/div/div[1]/div/div[3]/div[3]/div/a')
            email_full = email_element_xpath.get_attribute('href').replace('mailto:', '')
            job_data['Email'] = email_full.split('?')[0]  # Chỉ lấy phần trước dấu '?'
        except Exception as ex:
            print(f"Error getting Email with XPath 1: {ex}")
            # Thử tiếp bằng cách sử dụng selector mà bạn cung cấp thêm
            try:
                email_element_fallback = driver.find_element(By.CSS_SELECTOR, 'body > div.wrapper > div.container.root-container > div > div.content.th-content.js-content > div.row > div.col-md-4 > div > div:nth-child(2) > div > div.card.border-0.mb-3.card-expose-contact-info.ci-employer.th-card.th-card-expose-contact-info.ci-employer.clearfix > div > div:nth-child(3) > div.email a')
                email_full = email_element_fallback.get_attribute('href').replace('mailto:', '')
                job_data['Email'] = email_full.split('?')[0]  # Chỉ lấy phần trước dấu '?'
            except Exception as fallback_ex:
                print(f"Error getting Email with fallback CSS_SELECTOR: {fallback_ex}")

    # Lấy thông tin Telefon từ thẻ chứa số điện thoại
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

# Gọi hàm với URL cụ thể
get_contact_info('https://jobs.ausbildungsheld.de/stellenangebot/ausbildung-zur-zum-pflegefachfrau-pflegefachmann-BS3MY9')