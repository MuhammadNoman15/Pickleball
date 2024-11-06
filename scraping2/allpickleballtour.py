from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from datetime import datetime
import time
# Setup function for the driver
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

# Function to get tournament URLs
def get_tournament_urls(driver, url):
    driver.get(url)
    all_urls = []  # To collect URLs from all pages

    try:
        # Wait for the container to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "clearfix")))

        # Scroll to the bottom in case pagination is not immediately visible
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # Wait for the pagination block to be visible
        pagination_block = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div#searchPagination ul.pagination"))
        )
        
        # Get pagination links
        pagination_links = pagination_block.find_elements(By.CSS_SELECTOR, "li.page-item a.page-link")

        # Iterate over each pagination link
        for i in range(len(pagination_links)):
            pagination_block = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div#searchPagination ul.pagination"))
            )
            pagination_links = pagination_block.find_elements(By.CSS_SELECTOR, "li.page-item a.page-link")
            
            # Click on the pagination link
            pagination_links[i].click()

            # Wait for the page to load after clicking
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "clearfix")))

            # Locate all tournament rows on the current page
            tournament_rows = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.clearfix table tbody tr"))
            )

            # Extract URLs on the current page
            for row in tournament_rows:
                try:
                    td_elements = row.find_elements(By.TAG_NAME, "td")
                    if len(td_elements) > 1:
                        name_element = td_elements[1].find_element(By.TAG_NAME, "a")
                        details_url = name_element.get_attribute("href")
                        all_urls.append(details_url)

                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

            # Brief pause
            time.sleep(2)

        # Save URLs to a file
        with open("total_tournament_urls.txt", "w") as file:
            for url in all_urls:
                file.write(url + "\n")

        print(f"Total URLs collected and saved to 'tournament_urls.txt': {len(all_urls)}")
        return all_urls

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def format_date(date_str):
    # Convert date from MM/DD/YYYY to datetime object
    date_obj = datetime.strptime(date_str, "%m/%d/%Y")
    # Format the date to MMM DD, YYYY
    return date_obj.strftime("%b %d, %Y")


def extract_event_details(driver, url):
    driver.get(url)

    try:
        # Wait for the event details section to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "eventDetailsMain")))

        # Extract tournament name
        tournament_name = driver.find_element(By.CSS_SELECTOR, "div#eventDetailsMain h2").text.strip()

        # Extract date from the third and fourth <li> elements
        date_elements = driver.find_elements(By.CSS_SELECTOR, "div#eventDetailsMain ul.list-unstyled.manufacturer li")
        print(len(date_elements))
        if len(date_elements) >= 4:
            start_date = date_elements[2].find_element(By.TAG_NAME, "a").text.strip()  # Third <li>
            end_date = date_elements[3].find_element(By.TAG_NAME, "a").text.strip()    # Fourth <li>

            # Format dates
            start_date = format_date(start_date)
            end_date = format_date(end_date)
            date_text = f"{start_date} - {end_date}"
            
        else:
            date_text = "Date not found"

        # Extract location from the last <li>
        location_item = date_elements[4]  # Last <li>
        location_parts = location_item.find_elements(By.TAG_NAME, "a")

# Extract text from each location part and join them
        if location_parts:
            location = ", ".join(part.text.strip() for part in location_parts)
        else:
            location = "Location not found"

        # Print to debug
        print("Location parts:", [part.text.strip() for part in location_parts])
        print("Location:", location)

        # Extract hosting facility from the second <li> in the options section
        hosting_facility_element = driver.find_element(By.CSS_SELECTOR, "div#eventDetailsMain div.options ul.list-unstyled.manufacturer li:nth-child(2)").text
        hosting_facility = hosting_facility_element.split(":", 1)[1].strip()  # Split only at the first colon

# Print to debug
        print("Hosting Facility:", hosting_facility)


        # # Print to debug
        # print("Hosting Facility:", hosting_facility)

        return {
            "Name of Tournament": tournament_name,
            "Location": location,
            "Date": date_text,
            "Hosting Facility": hosting_facility
        }

    except Exception as e:
        print(f"An error occurred while extracting event details: {e}")
        return None

# Main script to use the functions and save data to an Excel file
if __name__ == "__main__":
    driver = setup_driver()

    # Commenting out the call to get tournament URLs for now
    # url = "https://www.allpickleballtournaments.com/search-pickleball.asp?countryIDs=1&endDate=03/15/2025"
    # tournament_urls = get_tournament_urls(driver, url)

    # Read tournament URLs from the file
    with open("total_tournament_urls_500_1000.txt", "r") as file:
        tournament_urls = [line.strip() for line in file if line.strip()]  # Read each line and strip whitespace

    # Create a DataFrame to store tournament data
    tournaments_data = []

    for tournament_url in tournament_urls:
        details = extract_event_details(driver, tournament_url)
        if details:
            tournaments_data.append(details)

            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(tournaments_data)

            # Save to Excel
            df.to_excel("total_tournament_urls_500_1000.xlsx", index=False)

    print("Tournament details have been saved to 'tournament_details.xlsx'.")
    driver.quit()

