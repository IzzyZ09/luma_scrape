import requests
from bs4 import BeautifulSoup
import csv

# input luma event URL
BASE_URL = input("Enter the Luma event URL (e.g. https://lu.ma/my-event): ").strip()

def get_attendees(event_url):
    res = requests.get(event_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    seen = set()
    attendees = []
    for link in soup.select('a[href^="/user/"]'):
        href = link.get('href')
        url = href if href.startswith('http') else 'https://lu.ma' + href
        if url in seen:
            continue
        seen.add(url)
        attendees.append({
            'name': link.get_text(strip=True),
            'profileUrl': url
        })
    return attendees

def get_linkedin(profile_url):
    try:
        res = requests.get(profile_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        social_links = soup.select('.social-links a')
        for a in social_links:
            href = a.get('href', '')
            if 'linkedin.com' in href:
                return href
        return ''
    except Exception:
        return ''

def main():
    attendees = get_attendees(BASE_URL)
    rows = [['Name', 'Profile URL', 'LinkedIn']]
    for attendee in attendees:
        linkedin = get_linkedin(attendee['profileUrl'])
        if linkedin:
            rows.append([attendee['name'], attendee['profileUrl'], linkedin])
            print(f"✅ Yes LinkedIn: {attendee['name']}")
        else:
            print(f"❌ No LinkedIn: {attendee['name']}")

    with open('luma_attendees_linkedin.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print("✅ CSV saved as luma_attendees_linkedin.csv")

if __name__ == "__main__":
    main()
