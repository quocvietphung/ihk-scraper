import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
import time
import random

def clean_text(text):
    """Làm sạch văn bản bằng cách loại bỏ khoảng trắng và các từ không cần thiết."""
    return ' '.join(text.split()).strip()

def format_phone_number(phone):
    """Định dạng lại số điện thoại theo chuẩn Đức và thay thế số 0 đầu tiên bằng +49."""
    digits_only = ''.join(filter(lambda x: x.isdigit() or x == '+', phone))
    if digits_only.startswith('0'):
        digits_only = '+49' + digits_only[1:]
    return digits_only if len(digits_only) >= 7 else ""

def clean_phone_format(phone):
    """Loại bỏ các ký tự đặc biệt như khoảng trắng, dấu gạch ngang, gạch chéo và định dạng lại số điện thoại."""
    cleaned_phone = phone.replace('-', '').replace('/', '').replace(' ', '')
    return format_phone_number(cleaned_phone)

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
    return ""  # Trả về chuỗi trống nếu không có dữ liệu

def extract_branche(soup):
    """Trích xuất thông tin Branche từ thẻ <h1>."""
    branche_element = soup.find('h1')
    if branche_element:
        return clean_text(branche_element.get_text(strip=True))
    return ""  # Trả về chuỗi trống nếu không có dữ liệu

def extract_contact_info(soup):
    """Trích xuất thông tin liên hệ từ hộp liên hệ trong HTML."""
    contact_info = {
        "Adresse": "",
        "Telefonnumer": "",
        "Email": "",
        "Unternehmen": "",
        "Anrede": "",
        "Vorname": "",
        "Nachname": ""
    }

    contact_section = soup.find('div', class_='contactBox')
    if contact_section:
        # Trích xuất địa chỉ
        address = contact_section.find('p')
        if address:
            contact_info["Adresse"] = clean_text(address.get_text(strip=True))

        # Trích xuất số điện thoại
        phone = contact_section.find('p', text=lambda t: t and 'Tel.' in t)
        if phone:
            raw_phone = clean_text(phone.get_text(strip=True).replace('Tel.', '').strip())
            contact_info["Telefonnumer"] = clean_phone_format(raw_phone)

        # Trích xuất email
        email = contact_section.find('a', href=lambda href: href and 'mailto:' in href)
        if email:
            contact_info["Email"] = email['href'].replace('mailto:', '').strip()

        # Trích xuất tên công ty (Unternehmen)
        unternehmen = contact_section.find('h3')
        if unternehmen:
            contact_info["Unternehmen"] = clean_text(unternehmen.get_text(strip=True))

        # Trích xuất Anrede, Vorname và Nachname
        person_label = contact_section.find('h3', text=lambda x: "Auf Deine Bewerbung freut sich" in x)
        if person_label:
            person_name = person_label.find_next('p')
            if person_name:
                full_name = clean_text(person_name.get_text(strip=True))

                # Tách các phần của tên
                parts = full_name.split()
                if len(parts) > 1:
                    contact_info["Nachname"] = parts[-1]  # Tên cuối cùng là Nachname
                    contact_info["Vorname"] = ' '.join(parts[:-1])  # Tất cả các từ trước đó là Vorname
                    if parts[0] in ["Herr", "Frau"]:
                        contact_info["Anrede"] = parts[0]
                        contact_info["Vorname"] = ' '.join(parts[1:-1])  # Loại bỏ Anrede khỏi Vorname
                else:
                    contact_info["Vorname"] = full_name  # Nếu chỉ có một từ

    return contact_info

def extract_additional_offers(soup):
    """Trích xuất các đề nghị bổ sung từ HTML nếu có."""
    additional_offers = [link.get_text(strip=True) for link in soup.select('ul.linkList li a')]
    return ', '.join(additional_offers) if additional_offers else ""  # Trả về chuỗi trống nếu không có dữ liệu

def scrape_job_details(job_url):
    """Scrape chi tiết công việc từ một URL nhất định."""
    session = requests.Session()
    retries = 3  # Số lần thử lại nếu gặp lỗi kết nối
    for i in range(retries):
        try:
            response = session.get(job_url, timeout=20)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.content, 'html.parser')

            job_details = OrderedDict([
                ("Angebots-Nr.", safe_extract(soup, 'Angebots-Nr.')),
                ("Branche", extract_branche(soup)),
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

        except requests.exceptions.ReadTimeout as e:
            print(f"Lỗi timeout cho {job_url}: {e}")
            time.sleep(random.uniform(1, 5))  # Tạm dừng ngẫu nhiên trước khi thử lại
        except requests.exceptions.ConnectionError as e:
            print(f"Thử lần {i + 1} thất bại cho {job_url}: {e}")
            time.sleep(random.uniform(1, 5))  # Tạm dừng ngẫu nhiên trước khi thử lại
        except Exception as e:
            print(f"Lỗi bất ngờ cho {job_url}: {e}")
            break
    return None  # Trả về None nếu tất cả các lần thử đều thất bại

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
            if job_details:
                jobs.append(job_details)

    return jobs

def scrape_ihk_pages(base_url, output_csv, start_page=0, end_page=1356):
    """Scrape nhiều trang danh sách công việc và lưu vào file CSV."""
    with open(output_csv, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=[
            "Angebots-Nr.", "Branche", "Unternehmen", "Stellenbeschreibung",
            "Schulabschluss wünschenswert", "gewünschte Vorqualifikation",
            "Beginn", "Angebotene Plätze", "Adresse", "Anrede", "Vorname", "Nachname",
            "Telefonnumer", "Email", "Weitere Ausbildungsplatzangebote", "URL"
        ])

        writer.writeheader()

        for page_num in range(start_page, end_page + 1):
            page_url = f"{base_url}&page={page_num}"
            response = requests.get(page_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs_on_page = scrape_job_list(soup)

                if not jobs_on_page:
                    print(f"Không còn công việc mới trên trang {page_num}. Dừng scrape.")
                    break

                for job in jobs_on_page:
                    writer.writerow(job)

                print(f"Trang {page_num} đã được scrape thành công với {len(jobs_on_page)} công việc.")
            else:
                print(f"Không thể truy cập trang {page_num}. Dừng scrape.")
                break

            time.sleep(1)

if __name__ == "__main__":
    base_url = 'https://www.ihk-lehrstellenboerse.de/angebote/suche?hitsPerPage=10&sortColumn=-1&sortDir=asc&query=Gib+Deinen+Wunschberuf+ein&organisationName=Unternehmen+eingeben&status=1&mode=0&dateTypeSelection=LASTCHANGED_DATE&thisYear=true&nextYear=true&afterNextYear=true&distance=0'

    output_csv = 'ihk_jobs.csv'
    scrape_ihk_pages(base_url, output_csv, start_page=0, end_page=1356)

    print("Quá trình scraping đã hoàn tất.")
