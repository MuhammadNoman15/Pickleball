from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

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

# Main scraping function
def scrape_event_links():
    driver = setup_driver()
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

    # Append links to a text file
    with open("EventBrite_Links_50.txt", "a") as file:
        for link in links:
            file.write(f"{link}\n")
    
    driver.quit()
    print("Link scraping complete. Saved to EventBrite_Links.txt")

# Run the scraping function
scrape_event_links()