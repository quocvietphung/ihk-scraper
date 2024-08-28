import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

def clean_text(text):
    return ' '.join(text.split()).replace('(Donau)', '').strip()

def scrape_job_details(job_url):
    response = requests.get(job_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    def safe_extract(label_text):
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

    # Sử dụng OrderedDict để đảm bảo thứ tự key
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

def scrape_ihk_data(url):
    base_url = "https://www.ihk-lehrstellenboerse.de"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    data = []

    for row in soup.select('table tbody tr'):
        relative_link = row.select_one('td:nth-child(1) a')['href']
        job_url = base_url + relative_link
        job_details = scrape_job_details(job_url)
        data.append(job_details)

    return data