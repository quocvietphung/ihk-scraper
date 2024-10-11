from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Cấu hình trình duyệt Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Khởi động trình duyệt
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Mở trang web
url = "https://www.ausbildung.de/berufe/pflegefachmann/stellen/#tab-bar-anchor"
driver.get(url)

# Đợi trang tải xong
time.sleep(1)

# Tìm và nhấn vào nút "Cookies zulassen"
try:
    accept_cookies_button = driver.find_element(By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
    accept_cookies_button.click()
    print("Đã chấp nhận cookie.")
except Exception as e:
    print("Không tìm thấy nút chấp nhận cookie hoặc đã có lỗi:", e)


# Hàm cuộn xuống cuối trang
def scroll_to_bottom():
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Đợi trang tải thêm dữ liệu


# Hàm nhấn nút "Weitere Ergebnisse laden" nếu nút xuất hiện
def click_load_more_button():
    try:
        load_more_button = driver.find_element(By.CSS_SELECTOR, 'div.btn-outline.btn-outline--meteor')
        if load_more_button.is_displayed():
            load_more_button.click()
            time.sleep(3)  # Đợi dữ liệu tải xong sau khi nhấn nút
            return True
    except:
        return False
    return False


# Cuộn và tải tất cả kết quả
def load_all_results():
    previous_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        scroll_to_bottom()  # Cuộn xuống cuối trang

        # Nhấn vào nút tải thêm kết quả nếu có
        if not click_load_more_button():
            current_height = driver.execute_script("return document.body.scrollHeight")

            # Kiểm tra nếu không có nội dung mới được tải
            if current_height == previous_height:
                break  # Thoát khỏi vòng lặp khi đã cuộn hết trang
            previous_height = current_height


# Thực hiện cuộn và tải tất cả kết quả
load_all_results()

# Đóng trình duyệt
driver.quit()

print("Đã tải xong tất cả kết quả.")
