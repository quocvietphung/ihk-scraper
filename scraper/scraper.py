import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
import time
import random

def clean_text(text):
    """Làm sạch văn bản bằng cách loại bỏ khoảng trắng và các từ không cần thiết."""
    return ' '.join(text.split()).replace('(Donau)', '').strip()

def safe_extract(soup, label_text):
    """Trích xuất thông tin một cách an toàn dựa trên nhãn từ HTML."""
    element = soup.find('td', text=label_text)
    if element:
        next_element = element.find_next('td')
        if next_element:
            if next_element.find('ul'):
                list_items = next_element.find_all('li')
                return ', '.join([li.get_text(strip=True) for li in list_items])
            else:
                return clean_text(next_element.get_text(strip=True))
    return "N/A"

def extract_beruf(soup):
    """Trích xuất thông tin Beruf từ thẻ <h1>."""
    beruf_element = soup.find('h1')
    if beruf_element:
        return clean_text(beruf_element.get_text(strip=True))
    return "N/A"

def extract_contact_info(soup):
    """Trích xuất thông tin liên hệ từ hộp liên hệ trong HTML."""
    contact_info = {"Adresse": "N/A", "Telefon": "N/A", "Email": "N/A", "Unternehmen": "N/A"}

    contact_section = soup.find('div', class_='contactBox')
    if contact_section:
        # Trích xuất địa chỉ
        address = contact_section.find('p')
        if address:
            contact_info["Adresse"] = clean_text(address.get_text(strip=True))

        # Trích xuất số điện thoại
        phone = contact_section.find('p', text=lambda t: t and 'Tel.' in t)
        if phone:
            contact_info["Telefon"] = clean_text(phone.get_text(strip=True).replace('Tel.', '').strip())

        # Trích xuất email
        email = contact_section.find('a', href=lambda href: href and 'mailto:' in href)
        if email:
            contact_info["Email"] = email['href'].replace('mailto:', '').strip()

        # Trích xuất tên công ty (Unternehmen)
        unternehmen = contact_section.find('h3')
        if unternehmen:
            contact_info["Unternehmen"] = clean_text(unternehmen.get_text(strip=True))

    return contact_info

def extract_additional_offers(soup):
    """Trích xuất các đề nghị bổ sung từ HTML nếu có."""
    additional_offers = [link.get_text(strip=True) for link in soup.select('ul.linkList li a')]
    return ', '.join(additional_offers) if additional_offers else 'N/A'

def scrape_job_details(job_url):
    """Scrape chi tiết công việc từ một URL nhất định."""
    session = requests.Session()
    retries = 3
    for i in range(retries):
        try:
            response = session.get(job_url, timeout=10)
            response.encoding = 'utf-8'  # Đảm bảo phản hồi được xử lý dưới dạng UTF-8
            soup = BeautifulSoup(response.content, 'html.parser')

            job_details = OrderedDict([
                ("Angebots-Nr.", safe_extract(soup, 'Angebots-Nr.')),
                ("Beruf", extract_beruf(soup)),  # Sử dụng hàm mới để trích xuất Beruf
                ("Unternehmen", safe_extract(soup, "Unternehmen")),
                ("Stellenbeschreibung", safe_extract(soup, 'Stellenbeschreibung')),
                ("Schulabschluss wünschenswert", safe_extract(soup, 'Schulabschluss wünschenswert')),
                ("gewünschte Vorqualifikation", safe_extract(soup, 'gewünschte Vorqualifikation')),
                ("Beginn", safe_extract(soup, 'Beginn')),
                ("Angebotene Plätze", safe_extract(soup, 'Angebotene Plätze')),
            ])

            contact_info = extract_contact_info(soup)
            job_details.update(contact_info)
            job_details["Weitere Ausbildungsplatzangebote"] = extract_additional_offers(soup)
            job_details["URL"] = job_url

            return job_details

        except requests.exceptions.ConnectionError as e:
            print(f"Thử lần {i+1} thất bại cho {job_url}: {e}")
            time.sleep(random.uniform(1, 5))  # Thử lại sau một khoảng thời gian ngẫu nhiên
        except Exception as e:
            print(f"Lỗi bất ngờ cho {job_url}: {e}")
            break
    return None  # Trả về None hoặc xử lý nếu tất cả các lần thử đều thất bại

def scrape_job_list(soup):
    """Scrape danh sách công việc từ HTML trang chính."""
    base_url = "https://www.ihk-lehrstellenboerse.de"
    jobs = []

    rows = soup.select('table tbody tr')
    if not rows:
        print("Không tìm thấy công việc nào trong bảng kết quả.")
    else:
        for row in rows:
            relative_link = row.select_one('td:nth-child(1) a')['href']
            job_url = base_url + relative_link
            job_details = scrape_job_details(job_url)
            if job_details:  # Chỉ thêm nếu không có lỗi
                jobs.append(job_details)

    return jobs

def scrape_ihk_pages(base_url, output_csv, start_page=1):
    """Scrape nhiều trang danh sách công việc và lưu vào file CSV."""
    with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as file:  # Mở file ở chế độ ghi mới (overwrite)
        writer = csv.DictWriter(file, delimiter=';', fieldnames=[
            "Angebots-Nr.", "Beruf", "Unternehmen", "Stellenbeschreibung", "Schulabschluss wünschenswert",
            "gewünschte Vorqualifikation", "Beginn", "Angebotene Plätze", "Adresse",
            "Telefon", "Email", "Weitere Ausbildungsplatzangebote", "URL"])

        writer.writeheader()

        page_num = start_page
        max_jobs_per_page = 10  # Số lượng công việc tối đa trên mỗi trang
        while True:
            page_url = f"{base_url}&page={page_num}"
            response = requests.get(page_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs_on_page = scrape_job_list(soup)

                if not jobs_on_page or len(jobs_on_page) < max_jobs_per_page:
                    print(f"Không còn công việc mới trên trang {page_num}. Dừng scrape và chuyển sang từ khóa tiếp theo.")
                    break

                for job in jobs_on_page:
                    writer.writerow(job)

                print(f"Trang {page_num} đã được scrape thành công với {len(jobs_on_page)} công việc.")
                page_num += 1
            else:
                print(f"Không thể truy cập trang {page_num}. Dừng scrape.")
                break

            time.sleep(1)  # Tạm dừng giữa các yêu cầu để tránh quá tải server

if __name__ == "__main__":
    for beruf in ["Hotelfachfrau", "Koch", "Pflege"]:
        base_url = (f'https://www.ihk-lehrstellenboerse.de/angebote/suche?hitsPerPage=10&'
                    f'sortColumn=-1&sortDir=asc&query={beruf}&status=1&mode=0&'
                    'dateTypeSelection=LASTCHANGED_DATE&thisYear=true&nextYear=true&afterNextYear=true&distance=0')

        output_csv = f'ihk_{beruf.lower()}_jobs.csv'  # Tên file CSV để lưu kết quả
        scrape_ihk_pages(base_url, output_csv, start_page=1)

    print("Quá trình scraping đã hoàn tất.")