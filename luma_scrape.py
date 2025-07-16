import requests
from bs4 import BeautifulSoup
import csv
import time

BASE_URL = "https://your-luma-event-url.com"  # Replace with your event URL

def get_attendees(event_url):
    res = requests.get(event_url)
    soup = BeautifulSoup(res.text, 'html.parser')
    seen = set()
    attendees = []
    for link in soup.select('a[href^="/user/"]'):
        href = link.get('href')
        url = href if href.startswith('http') else BASE_URL + href
        if url in seen:
            continue
        seen.add(url)
        attendees.append({
            'name': link.get_text(strip=True),
            'profileUrl': url
        })
    return attendees

def get_social_links(profile_url):
    try:
        res = requests.get(profile_url)
        soup = BeautifulSoup(res.text, 'html.parser')
        social_links = soup.select('.social-links a')
        result = {
            'instagram': '',
            'x': '',
            'tiktok': '',
            'linkedin': '',
            'website': ''
        }
        for a in social_links:
            href = a.get('href', '')
            if 'instagram.com' in href:
                result['instagram'] = href
            elif 'twitter.com' in href or 'x.com' in href:
                result['x'] = href
            elif 'tiktok.com' in href:
                result['tiktok'] = href
            elif 'linkedin.com' in href:
                result['linkedin'] = href
            elif 'lumacdn.com' not in href and 'lu.ma' not in href:
                result['website'] = href
        return result
    except Exception as e:
        return {
            'instagram': '',
            'x': '',
            'tiktok': '',
            'linkedin': '',
            'website': ''
        }

def main():
    event_url = BASE_URL  # Set your event page URL here
    attendees = get_attendees(event_url)
    rows = [['Name', 'Profile URL', 'Instagram', 'X', 'TikTok', 'LinkedIn', 'Website']]
    for attendee in attendees:
        socials = get_social_links(attendee['profileUrl'])
        rows.append([
            attendee['name'],
            attendee['profileUrl'],
            socials['instagram'],
            socials['x'],
            socials['tiktok'],
            socials['linkedin'],
            socials['website']
        ])
        print(f"Processed: {attendee['name']}")
        time.sleep(0.5)  # polite delay

    with open('luma_attendees_with_socials.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print("CSV file saved as luma_attendees_with_socials.csv")

if __name__ == "__main__":
    main() 
