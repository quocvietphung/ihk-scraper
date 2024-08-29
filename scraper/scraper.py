import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
import csv
import time

def clean_text(text):
    """Làm sạch chuỗi văn bản, loại bỏ khoảng trắng thừa và ký tự không cần thiết."""
    return ' '.join(text.split()).replace('(Donau)', '').strip()

def safe_extract(soup, label_text):
    """Trích xuất thông tin từ một nhãn cụ thể trong trang HTML."""
    element = soup.find('td', text=label_text)
    if element:
        next_element = element.find_next('td')
        if next_element.find('ul'):
            list_items = next_element.find_all('li')
            return ', '.join([li.get_text(strip=True) for li in list_items])
        else:
            return clean_text(next_element.get_text(strip=True))
    return "N/A"

def extract_contact_info(soup):
    """Trích xuất thông tin liên hệ từ trang HTML."""
    contact_info = {"Adresse": "N/A", "Telefon": "N/A", "Email": "N/A"}

    contact_section = soup.find('div', class_='contactBox')
    if contact_section:
        address = contact_section.find('p')
        if address:
            contact_info["Adresse"] = clean_text(address.get_text(strip=True))

        phone = contact_section.find('p', text=lambda t: t and 'Tel.' in t)
        if phone:
            contact_info["Telefon"] = clean_text(phone.get_text(strip=True).replace('Tel.', '').strip())

        email = contact_section.find('a', href=lambda href: href and 'mailto:' in href)
        if email:
            contact_info["Email"] = email['href'].replace('mailto:', '').strip()

    return contact_info

def extract_additional_offers(soup):
    """Trích xuất các đề nghị bổ sung từ trang HTML."""
    additional_offers = [link.get_text(strip=True) for link in soup.select('ul.linkList li a')]
    return ', '.join(additional_offers) if additional_offers else 'N/A'

def scrape_job_details(job_url):
    """Thu thập chi tiết công việc từ URL."""
    response = requests.get(job_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_details = OrderedDict([
        ("Angebots-Nr.", safe_extract(soup, 'Angebots-Nr.')),
        ("Stellenbeschreibung", safe_extract(soup, 'Stellenbeschreibung')),
        ("Schulabschluss wünschenswert", safe_extract(soup, 'Schulabschluss wünschenswert')),
        ("gewünschte Vorqualifikation", safe_extract(soup, 'gewünschte Vorqualifikation')),
        ("Beginn", safe_extract(soup, 'Beginn')),
        ("Angebotene Plätze", safe_extract(soup, 'Angebotene Plätze')),
    ])

    # Thêm thông tin liên hệ và các đề nghị bổ sung
    contact_info = extract_contact_info(soup)
    job_details.update(contact_info)
    job_details["Weitere Ausbildungsplatzangebote"] = extract_additional_offers(soup)
    job_details["URL"] = job_url

    return job_details

def scrape_job_list(soup):
    """Thu thập danh sách công việc từ một trang HTML."""
    base_url = "https://www.ihk-lehrstellenboerse.de"
    jobs = []

    for row in soup.select('table tbody tr'):
        relative_link = row.select_one('td:nth-child(1) a')['href']
        job_url = base_url + relative_link
        job_details = scrape_job_details(job_url)
        jobs.append(job_details)

    return jobs

def scrape_ihk_pages(base_url, total_pages, output_csv):
    """Duyệt qua tất cả các trang và lưu dữ liệu vào file CSV."""
    with open(output_csv, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, delimiter=';', fieldnames=[
            "Angebots-Nr.", "Stellenbeschreibung", "Schulabschluss wünschenswert",
            "gewünschte Vorqualifikation", "Beginn", "Angebotene Plätze", "Adresse",
            "Telefon", "Email", "Weitere Ausbildungsplatzangebote", "URL"])

        writer.writeheader()

        for page_num in range(1, total_pages + 1):
            page_url = f"{base_url}&page={page_num}"
            response = requests.get(page_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                jobs_on_page = scrape_job_list(soup)

                for job in jobs_on_page:
                    writer.writerow(job)

                print(f"Page {page_num} scraped successfully with {len(jobs_on_page)} job listings.")
            else:
                print(f"Failed to retrieve page {page_num}")

            time.sleep(1)  # Thời gian chờ giữa các yêu cầu để tránh quá tải server

if __name__ == "__main__":
    base_url = ('https://www.ihk-lehrstellenboerse.de/angebote/suche?hitsPerPage=10&'
                'sortColumn=-1&sortDir=asc&query=Gib+Deinen+Wunschberuf+ein&'
                'organisationName=Unternehmen+eingeben&status=1&mode=0&'
                'dateTypeSelection=LASTCHANGED_DATE&thisYear=true&nextYear=true&afterNextYear=true&distance=0')

    total_pages = 1682  # Tổng số trang cần scrape
    output_csv = 'ihk_jobs.csv'  # Tên file CSV để lưu kết quả

    scrape_ihk_pages(base_url, total_pages, output_csv)

    print(f"Scraping completed. Data saved to {output_csv}.")