import csv
import random
import asyncio
from playwright.async_api import async_playwright

# ---------- Load Rotating User Agents ----------
def load_user_agents(filename="user_agents.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

user_agents = load_user_agents()
listing_data = []
max_pages = 3

# ---------- Scraping Function ----------
async def scrape_page(page_url, page_number):
    selected_agent = random.choice(user_agents)
    records_scraped = 0
    next_page_url = None
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=selected_agent,
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True
        )
        page = await context.new_page()
        print(f"Navigating to page {page_number}: {page_url}")
        await page.goto(page_url, timeout=60000)
        await asyncio.sleep(random.uniform(5, 8))

        await page.wait_for_selector("div.listing-card-root", timeout=15000)
        listings = await page.query_selector_all("div.listing-card-root")
        print(f"Found {len(listings)} listings.")

        for idx, card in enumerate(listings, 1):
            try:
                link_elem = await card.query_selector("a.listing-card-link")
                title = await link_elem.get_attribute("title") if link_elem else "N/A"
                url = await link_elem.get_attribute("href") if link_elem else "N/A"
                price_elem = await card.query_selector("div.listing-price")
                price = await price_elem.inner_text() if price_elem else "N/A"
                address_elem = await card.query_selector("div.listing-address")
                address = await address_elem.inner_text() if address_elem else "N/A"
                location_elem = await card.query_selector("div.listing-location")
                location = await location_elem.inner_text() if location_elem else "N/A"

                feature_list = await card.query_selector_all("ul.listing-feature-group li.info-item span.info-value")
                feature_texts = []
                for f in feature_list:
                    txt = await f.inner_text()
                    if txt.strip():
                        feature_texts.append(txt.strip())

                features = {
                    "Bedrooms": feature_texts[0] if len(feature_texts) > 0 else "N/A",
                    "Bathrooms": feature_texts[1] if len(feature_texts) > 1 else "N/A",
                    "Floor Area": feature_texts[2] if len(feature_texts) > 2 else "N/A",
                    "Price per sqft": feature_texts[3] if len(feature_texts) > 3 else "N/A"
                }

                image_elem = await card.query_selector("img.hui-image[da-id='media-carousel-img']")
                image_url = await image_elem.get_attribute("src") if image_elem else "N/A"
                listing_data.append({
                    "Title": title,
                    "URL": url,
                    "Price": price,
                    "Address": address,
                    "Location": location,
                    "ImageURL": image_url,
                    "Bedrooms": features["Bedrooms"],
                    "Bathrooms": features["Bathrooms"],
                    "Floor Area": features["Floor Area"],
                    "Price per sqft": features["Price per sqft"]
                })

                records_scraped += 1
                print(f"Listing {idx}: {title[:50]}...")

            except Exception as e:
                print(f"Error on listing {idx}: {e}")

        # Scroll down to make pagination visible
        # await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # await asyncio.sleep(1)
        # Look for the next page element before constructing next_page_url
        next_page_url = None
        if page_number < max_pages:
            next_elem = await page.query_selector("a[da-id='hui-pagination-btn-next']")
            if next_elem:
                import re
                base_url = re.sub(r"/\d+$", "", page_url)
                next_page_url = f"{base_url}/{page_number+1}"

        await browser.close()
    return records_scraped, next_page_url



# ---------- Main Scraping Loop ----------
async def main():
    current_url = "https://www.propertyguru.com.sg/property-for-rent/1"
    page_num = 1
    total_records = 0
    max_records = 200

    while total_records < max_records and current_url:
        records_scraped, next_url = await scrape_page(current_url, page_num)
        total_records += records_scraped
        print(f"📦 Total listings collected: {total_records}")
        current_url = next_url
        page_num += 1
        await asyncio.sleep(random.uniform(10, 15))

    # ---------- Save Results ----------
    csv_file = "propertyguru_listings.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "Title", "URL", "Price", "Address", "Location", "ImageURL", "Bedrooms", "Bathrooms", "Floor Area", "Price per sqft"])
        writer.writeheader()
        writer.writerows(listing_data)

    print(f"Saved {len(listing_data)} listings to '{csv_file}'")

if __name__ == "__main__":
    asyncio.run(main())
