from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException

# Initialize the WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--log-level=3')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to scrape individual event details directly by class names
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



# Main function to read URLs and save scraped data to Excel
def scrape_from_urls_file():
    driver = setup_driver()
    
    # Load URLs from the file
    with open("EventBrite_Links_50.txt", "r") as file:
        urls = file.read().splitlines()
    
    # List to hold scraped event data
    event_data = []
    
    # Scrape data from each URL
    for url in urls:
        event_info = scrape_event_details(driver, url)
        if event_info:
            event_data.append(event_info)
    
    # Save scraped data to an Excel file
    df = pd.DataFrame(event_data)
    df.to_excel("newpage.xlsx", index=False)
    
    driver.quit()
    print("Scraping complete. Data saved to newpage.xlsx.")

# Run the main function
scrape_from_urls_file()
