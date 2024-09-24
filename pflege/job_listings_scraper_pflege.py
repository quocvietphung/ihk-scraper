import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

# Cấu hình Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")  # Chạy ở chế độ ẩn
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Tự động cài đặt và quản lý ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# URL bạn cần lấy dữ liệu
url = "https://www.ausbildung.de/suche/?form_main_search%5Brlon%5D=7.219&form_main_search%5Brlat%5D=51.2744&form_main_search%5Bvideo_application_on%5D=&form_main_search%5Bshow_integrated_degree_programs%5D=1&form_main_search%5Bshow_educational_trainings%5D=1&form_main_search%5Bshow_qualifications%5D=1&form_main_search%5Bshow_regular_apprenticeships%5D=1&form_main_search%5Bshow_inhouse_trainings%5D=1&form_main_search%5Bshow_educational_trainings_and_regular_apprenticeships%5D=1&form_main_search%5Bshow_training_programs%5D=1&form_main_search%5Bradius%5D=14&form_main_search%5Bmin_radius%5D=0&form_main_search%5Bprofession_public_id%5D=&form_main_search%5Bprofession_topic_public_id%5D=&form_main_search%5Bindustry_public_id%5D=&form_main_search%5Bexpected_graduation%5D=&form_main_search%5Bstarts_no_earlier_than%5D=&form_main_search%5Bsort_order%5D=relevance&form_main_search%5Bbreaker_tile%5D=true&form_main_search%5Bcorporation_promote_foreign_applications%5D=false&form_main_search%5Bwhat%5D=Pflegefachmann%2F-frau&form_main_search%5Bwhere%5D=42103+Wuppertal&t_search_type=main&t_what=Pflegefachmann%2F-frau&t_where=42103+Wuppertal"
driver.get(url)

# Đợi trang tải xong
time.sleep(5)

# Hàm lấy lại danh sách các phần tử
def get_job_links():
    return driver.find_elements(By.CSS_SELECTOR, 'a.job-posting-cluster-cards__link')

# Tạo tệp CSV và mở chế độ ghi
with open('job_links.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Branche', 'Website'])  # Viết tiêu đề cột

    # Lấy các liên kết công việc
    job_links = get_job_links()

    # Lặp qua từng công việc và mở URL
    for index in range(len(job_links)):
        job_links = get_job_links()  # Lấy lại các phần tử trên trang để tránh lỗi stale element
        job = job_links[index]  # Lấy phần tử hiện tại

        job_url = job.get_attribute("href")
        print(f"Website {index + 1}: {job_url}")

        # Mở từng URL
        driver.get(job_url)

        # Đợi trang mới tải xong
        time.sleep(3)

        # Lấy tiêu đề công việc
        try:
            job_title = driver.find_element(By.CSS_SELECTOR, 'h1').text  # Tùy vào cấu trúc HTML của trang chi tiết
        except:
            job_title = "N/A"  # Nếu không tìm thấy tiêu đề

        print(f"Branche: {job_title}")

        # Ghi dữ liệu vào tệp CSV
        writer.writerow([job_title, job_url])

        # Quay trở lại trang tìm kiếm ban đầu
        driver.get(url)
        time.sleep(3)

# Đóng trình duyệt sau khi hoàn thành
driver.quit()

print("Đã lưu dữ liệu vào file job_links.csv")
