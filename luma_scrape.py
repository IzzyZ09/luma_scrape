import csv
from playwright.sync_api import sync_playwright

def scrape_luma(event_url):
    rows = [['Name', 'Profile URL', 'LinkedIn']]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Change to True to run invisibly
        context = browser.new_context()
        page = context.new_page()

        print(f"🔗 Opening event: {event_url}")
        page.goto(event_url)

        # Step 1: Click the guest list button ("93 others")
        try:
            more_btn = page.locator("button.guests-button")
            if more_btn.is_visible():
                print("📌 Clicking guest list to expand attendees...")
                more_btn.click()
                page.wait_for_timeout(2000)
            else:
                print("⚠️ Guest list button not visible.")
        except Exception as e:
            print("⚠️ Could not click guest list button:", e)

        # Step 2: Grab attendee links
        print("🔍 Collecting attendee links...")
        attendee_links = page.locator('a[href^="/user/"]')
        count = attendee_links.count()
        print(f"Found {count} attendees.")

        seen = set()
        attendees = []

        for i in range(count):
            link = attendee_links.nth(i)
            href = link.get_attribute("href")
            name = link.inner_text().strip()
            full_url = href if href.startswith("http") else "https://lu.ma" + href
            if full_url not in seen:
                seen.add(full_url)
                attendees.append({
                    "name": name,
                    "profileUrl": full_url
                })

        print(f"✅ Found {len(attendees)} unique attendees.")

        # Step 3: Visit each profile and grab LinkedIn
        for person in attendees:
            print(f"🌐 Visiting: {person['name']}")
            try:
                page.goto(person["profileUrl"])
                page.wait_for_timeout(800)
                social_links = page.locator('.social-links a')
                linkedin = ''
                for j in range(social_links.count()):
                    link = social_links.nth(j).get_attribute('href')
                    if link and 'linkedin.com' in link:
                        linkedin = link
                        break
                if linkedin:
                    rows.append([person["name"], person["profileUrl"], linkedin])
                    print(f"🔗 LinkedIn: {linkedin}")
                else:
                    print("❌ No LinkedIn found.")
            except Exception as e:
                print(f"⚠️ Error visiting {person['profileUrl']}: {e}")

        browser.close()

    # Step 4: Save CSV
    with open('luma_attendees_linkedin_only.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print("📁 Done! Saved as luma_attendees_linkedin_only.csv")

# Run it
if __name__ == "__main__":
    event_url = input("Paste the full Luma event URL: ").strip()
    scrape_luma(event_url)
