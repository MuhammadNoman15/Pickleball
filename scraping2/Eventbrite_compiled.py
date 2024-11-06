from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Initialize the WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "safebrowsing.enabled": "true",
        "profile.managed_default_content_settings.images": 2  # Disable images for faster loading
    }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to scrape event links
def scrape_event_links(driver):
    base_url = "https://www.eventbrite.com/d/united-states/pickleball/?page={}"
    links = []
    wait = WebDriverWait(driver, 20)

    # Loop through pages 1 to 50
    for page_num in range(1, 8):
        url = base_url.format(page_num)
        driver.get(url)

        try:
            # Locate the ul tag that contains all event li elements
            ul_element = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "ul.SearchResultPanelContentEventCardList-module__eventList___2wk-D")
            ))

            # Locate all li tags inside the ul
            event_cards = ul_element.find_elements(By.TAG_NAME, "li")

            # Loop through each event card to extract URLs
            for card in event_cards:
                try:
                    # Navigate through the nested structure to find the details section
                    details_section = card.find_element(By.CSS_SELECTOR, "section.DiscoverHorizontalEventCard-module__cardWrapper___2_FKN section.event-card-details")
                    
                    # Find the link in the nested <a> tag
                    event_link_tag = details_section.find_element(By.CSS_SELECTOR, "a.event-card-link")
                    tournament_link = event_link_tag.get_attribute("href")

                    # Append the link to the links list for saving
                    links.append(tournament_link)

                except Exception as e:
                    print(f"Error scraping individual event link on page {page_num}: {e}")
                    continue
        except Exception as e:
            print(f"Error locating event cards on page {page_num}: {e}")

    return links

# Function to scrape individual event details
def scrape_event_details(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    try:
        # Locate the main content div
        main_content_div = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div.Layout-module__module___2eUcs.Layout-module__mainContent___1b1nj")
        ))

        # Extract the tournament name
        tournament_name_element = main_content_div.find_element(By.CLASS_NAME, "event-title")
        tournament_name = tournament_name_element.text

        # Extract the date
        event_date_element = main_content_div.find_element(By.CLASS_NAME, "start-date")
        event_date = event_date_element.get_attribute("datetime")

        # Extract the location details
        location_info_element = main_content_div.find_element(By.CLASS_NAME, "location-info__address")
        location = location_info_element.find_element(By.CLASS_NAME, "location-info__address-text").text
        
        # Extract the facility name by getting all text from the location_info_element
        facility_name = location_info_element.text.replace(location, '').strip()
        facility_name = facility_name.replace("Show map", "").strip()

        # Return the structured scraped data
        return {
            "Name of Tournament": tournament_name,
            "Location": location,
            "Date": event_date,
            "Facility Name": facility_name
        }

    except Exception as e:
        print(f"Error scraping event details from {url}: {e}")
        return None

# Main function to scrape event links and details, and save to Excel
def main():
    driver = setup_driver()
    
    # Step 1: Scrape all event links
    links = scrape_event_links(driver)
    print(f"Scraped {len(links)} links.")

    # Step 2: Scrape event details from each link
    event_data = []
    for url in links:
        event_info = scrape_event_details(driver, url)
        if event_info:
            event_data.append(event_info)

    # Step 3: Save scraped data to an Excel file
    if event_data:
        df = pd.DataFrame(event_data)
        df.to_excel("newpage_compiled.xlsx", index=False)
        print("Scraping complete. Data saved to newpage.xlsx.")
    else:
        print("No data scraped.")

    driver.quit()

# Run the main function
if __name__ == "__main__":
    main()
