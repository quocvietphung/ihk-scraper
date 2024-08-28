import requests
from bs4 import BeautifulSoup

def clean_text(text):
    """Hàm để làm sạch chuỗi văn bản: xóa các khoảng trắng và ký tự xuống dòng."""
    return ' '.join(text.split()).replace('(Donau)', '').strip()

def scrape_job_details(job_url):
    """Scrape detailed job information from the job detail page."""
    response = requests.get(job_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Helper function to safely extract data
    def safe_extract(label_text):
        element = soup.find('td', text=label_text)
        if element:
            next_element = element.find_next('td')
            # Check if the next element contains a list
            if next_element.find('ul'):
                list_items = next_element.find_all('li')
                return ', '.join([li.get_text(strip=True) for li in list_items])
            else:
                return clean_text(next_element.get_text(strip=True))
        return "N/A"  # Return "N/A" if the element is not found

    # Extract the required details using safe_extract
    angebot_nr = safe_extract('Angebots-Nr.')
    schulabschluss = safe_extract('Schulabschluss wünschenswert')
    vorqualifikation = safe_extract('gewünschte Vorqualifikation')
    beginn = safe_extract('Beginn')
    plaetze = safe_extract('Angebotene Plätze')
    stellenbeschreibung = safe_extract('Stellenbeschreibung')

    # Tìm phần "Kontakt"
    kontakt_info_section = soup.find('div', class_='contactBox')

    # Tìm địa chỉ trong phần "Kontakt"
    address = "N/A"
    if kontakt_info_section:
        address_p = kontakt_info_section.find('p')
        if address_p:
            address = clean_text(address_p.get_text(strip=True))

    # Tìm số điện thoại trong phần "Kontakt"
    tel = "N/A"
    if kontakt_info_section:
        tel_p = kontakt_info_section.find('p', text=lambda t: t and 'Tel.' in t)
        if tel_p:
            tel = clean_text(tel_p.get_text(strip=True).split(':')[-1].strip())

    # Tìm email trong phần "Kontakt"
    email = "N/A"
    email_a = kontakt_info_section.find('a', href=lambda href: href and 'mailto:' in href)
    if email_a:
        email = email_a['href'].replace('mailto:', '').strip()

    # Lấy thêm các vị trí khác của công ty (nếu có)
    weitere_angebote = []
    for link in soup.select('ul.linkList li a'):
        weitere_angebote.append(link.get_text(strip=True))
    weitere_angebote = ', '.join(weitere_angebote) if weitere_angebote else 'N/A'

    return {
        "Angebots-Nr.": angebot_nr,
        "URL": job_url,
        "Schulabschluss wünschenswert": schulabschluss,
        "gewünschte Vorqualifikation": vorqualifikation,
        "Beginn": beginn,
        "Angebotene Plätze": plaetze,
        "Stellenbeschreibung": stellenbeschreibung,
        "Adresse": address,
        "Telefon": tel,
        "Email": email,
        "Weitere Ausbildungsplatzangebote": weitere_angebote
    }

def scrape_ihk_data(url):
    """Scrape job links from the main page and retrieve detailed job data."""
    base_url = "https://www.ihk-lehrstellenboerse.de"

    # Fetch the main page content
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []

    # Iterate over each job row to get the detail link
    for row in soup.select('table tbody tr'):
        # Get the relative link to the job detail page
        relative_link = row.select_one('td:nth-child(1) a')['href']
        job_url = base_url + relative_link  # Construct the full URL

        # Scrape the detailed job information from the job page
        job_details = scrape_job_details(job_url)

        # Add the scraped job details to the data list
        data.append(job_details)

    return data