import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
import time


def clean_text(text):
    """Hàm để làm sạch chuỗi văn bản: xóa các khoảng trắng và ký tự xuống dòng."""
    return ' '.join(text.split()).replace('(Donau)', '').strip()


def scrape_job_details(job_url):
    """Scrape chi tiết từng công việc từ trang chi tiết."""
    response = requests.get(job_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    def safe_extract(label_text):
        """Hàm phụ để lấy thông tin an toàn từ các thẻ HTML."""
        element = soup.find('td', text=label_text)
        if element:
            next_element = element.find_next('td')
            if next_element.find('ul'):
                list_items = next_element.find_all('li')
                return ', '.join([li.get_text(strip=True) for li in list_items])
            else:
                return clean_text(next_element.get_text(strip=True))
        return "N/A"

    angebot_nr = safe_extract('Angebots-Nr.')
    schulabschluss = safe_extract('Schulabschluss wünschenswert')
    vorqualifikation = safe_extract('gewünschte Vorqualifikation')
    beginn = safe_extract('Beginn')
    plaetze = safe_extract('Angebotene Plätze')
    stellenbeschreibung = safe_extract('Stellenbeschreibung')

    kontakt_info_section = soup.find('div', class_='contactBox')

    address = "N/A"
    if kontakt_info_section:
        address_p = kontakt_info_section.find('p')
        if address_p:
            address = clean_text(address_p.get_text(strip=True))

    tel = "N/A"
    if kontakt_info_section:
        tel_p = kontakt_info_section.find('p', text=lambda t: t and 'Tel.' in t)
        if tel_p:
            tel = clean_text(tel_p.get_text(strip=True).replace('Tel.', '').strip())

    email = "N/A"
    email_a = kontakt_info_section.find('a', href=lambda href: href and 'mailto:' in href)
    if email_a:
        email = email_a['href'].replace('mailto:', '').strip()

    weitere_angebote = []
    for link in soup.select('ul.linkList li a'):
        weitere_angebote.append(link.get_text(strip=True))
    weitere_angebote = ', '.join(weitere_angebote) if weitere_angebote else 'N/A'

    # Trả về dữ liệu theo thứ tự định trước
    return OrderedDict([
        ("Angebots-Nr.", angebot_nr),
        ("Stellenbeschreibung", stellenbeschreibung),
        ("Schulabschluss wünschenswert", schulabschluss),
        ("gewünschte Vorqualifikation", vorqualifikation),
        ("Beginn", beginn),
        ("Angebotene Plätze", plaetze),
        ("Adresse", address),
        ("Telefon", tel),
        ("Email", email),
        ("Weitere Ausbildungsplatzangebote", weitere_angebote),
        ("URL", job_url)
    ])


def scrape_job_list(soup):
    """Scrape danh sách công việc trên một trang."""
    job_list = []
    base_url = "https://www.ihk-lehrstellenboerse.de"

    for row in soup.select('table tbody tr'):
        relative_link = row.select_one('td:nth-child(1) a')['href']
        job_url = base_url + relative_link
        job_details = scrape_job_details(job_url)
        job_list.append(job_details)

    return job_list


def scrape_ihk_pages(base_url, total_pages, output_csv):
    """Duyệt qua tất cả các trang và lưu dữ liệu vào file CSV."""
    all_data = []

    # Mở file CSV để lưu kết quả
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Angebots-Nr.", "Stellenbeschreibung", "Schulabschluss wünschenswert",
            "gewünschte Vorqualifikation", "Beginn", "Angebotene Plätze", "Adresse",
            "Telefon", "Email", "Weitere Ausbildungsplatzangebote", "URL"])

        # Viết tiêu đề cho file CSV
        writer.writeheader()

        for page_num in range(total_pages + 1):
            page_url = f"{base_url}&page={page_num}"
            response = requests.get(page_url)

            if response.status_code != 200:
                print(f"Failed to retrieve page {page_num}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            jobs_on_page = scrape_job_list(soup)
            all_data.extend(jobs_on_page)

            # Ghi dữ liệu của mỗi trang vào CSV
            for job in jobs_on_page:
                writer.writerow(job)

            print(f"Page {page_num} scraped successfully with {len(jobs_on_page)} job listings.")
            time.sleep(1)  # Thời gian chờ giữa các yêu cầu để tránh quá tải server

    return all_data


# Main script execution
base_url = 'https://www.ihk-lehrstellenboerse.de/angebote/suche?hitsPerPage=10&sortColumn=-1&sortDir=asc&query=Gib+Deinen+Wunschberuf+ein&organisationName=Unternehmen+eingeben&status=1&mode=0&dateTypeSelection=LASTCHANGED_DATE&thisYear=true&nextYear=true&afterNextYear=true&distance=0'

total_pages = 1682  # Tổng số trang
output_csv = 'ihk_jobs.csv'  # Tên file CSV để lưu kết quả

# Duyệt qua tất cả các trang và lưu kết quả vào file CSV
scrape_ihk_pages(base_url, total_pages, output_csv)

print(f"Scraping completed. Data saved to {output_csv}.")