import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# Setup driver function
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--log-level=3')  # Suppress all logging
    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Disable notifications
        "safebrowsing.enabled": "true"  # Enable Safe Browsing
    }
    options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to fetch all event links and save to 'event_links.txt'
def fetch_event_links(url):
    driver = setup_driver()
    driver.get(url)

    # Wait for the initial content to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dvEventSearchList_v2"))
        )
        time.sleep(2)  # Additional wait to ensure all elements are loaded
    except Exception as e:
        print("Error loading the page:", e)
        driver.quit()
        return

    # Set a maximum number of attempts (clicks)
    max_clicks = 20  # Increase this number if necessary
    click_count = 0

    # Click the "See more" button until "No More Results" appears or the max number of clicks is reached
    while click_count < max_clicks:
        try:
            # Check if the "No More Results" div is visible
            no_more_results = driver.find_element(By.ID, "dvNoMoreResults")
            if no_more_results.is_displayed():
                print("No more results to load. Exiting loop.")
                break
        except Exception as e:
            print("'No More Results' div not found, continuing to load more results.")
        
        # Try clicking the "See more" button
        try:
            print("Attempting to click 'See more' button...")
            see_more_button = driver.find_element(By.ID, "btnMoreResults")
            driver.execute_script("arguments[0].click();", see_more_button)
            click_count += 1
            print(f"'See more' button clicked {click_count} times. Waiting for new results to load...")
            time.sleep(10)  # Increase wait time for new results to load
        except Exception as e:
            print("Error clicking 'See more' button:", e)
            break

    # After reaching max clicks or "No More Results," parse the page for event URLs
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Open file to write links
    event_urls = set()  # Use a set to avoid duplicates
    with open('event_links1.txt', 'w') as file:
        # Find the parent div by ID
        parent_div = soup.find('div', {'id': 'dvEventSearchList_v2'})
        if parent_div:
            # Find all divs with class "browse-row" within the parent div
            for browse_row in parent_div.find_all('div', class_='browse-row'):
                # Look for the child divs within browse-row that contain the 'onclick' attribute
                inner_div = browse_row.find('div', onclick=True)
                if inner_div:
                    onclick_attr = inner_div.get('onclick')
                    unique_id = onclick_attr.split("'")[1] if onclick_attr else None
                    if unique_id:
                        event_url = f"https://pickleballbrackets.com/ptd.aspx?eid={unique_id}"
                        event_urls.add(event_url)  # Add to the set to ensure uniqueness
                        print(f"Extracted URL: {event_url}")
        else:
            print("Parent div not found.")

        # Write all collected event URLs to the file
        for url in event_urls:
            file.write(url + '\n')

    print(f"Total unique event links fetched: {len(event_urls)}")
    print("Event links successfully written to event_links1.txt.")

# Function to scrape data from each event link
def scrape_event_data(url):
    driver = setup_driver()
    driver.get(url)

    # Wait for content to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "event-detail-content-inner"))
        )
        time.sleep(2)  # Extra wait for dynamic content
    except Exception as e:
        print(f"Error loading {url}: {e}")
        driver.quit()
        return None

    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Extract Tournament Name and Date
    tournament_name = ""
    date = ""
    location = "N/A"  # Default if location not found
    hosting_facility = "No Parking fee"

    # Find Tournament Name
    name_div = soup.find('div', class_='event-detail-content-inner').find('div', class_='p-25 b-b event-details-title')
    if name_div:
        tournament_name_tag = name_div.find('h1')
        if tournament_name_tag:
            tournament_name = tournament_name_tag.get_text(strip=True)

    # Find Date
    date_div = soup.find('div', class_='event-detail-content-inner').find('div', class_='event-details-info-head')
    if date_div:
        date_info = date_div.find('div', class_='event-details-main flex flex-center')
        if date_info:
            date_listing = date_info.find('div', class_='listing-date m-b-10 p-t-10')
            if date_listing:
                date_span = date_listing.find('span', class_='flex flex-middle')
                if date_span and date_span.find('span'):
                    date = date_span.find('span').get_text(strip=True)

    # Find Location
    location_div = soup.find('div', class_='event-detail-content-inner') \
        .find('div', class_='event-details-content-info m-l-15 m-r-15') \
        .find('div', class_='row flex') \
        .find('div', class_='event-info-expanded col-md-9 flex flex-col p-r-25 m-r-25') \
        .find('div', class_='tab-content') \
        .find('div', role='tabpanel') \
        .find('div', class_='font-600 font-md flex m-b-20')
    
    if location_div:
        location = location_div.get_text(strip=True)

    return {
        "Name of Tournament": tournament_name,
        "Location": location,
        "Date": date,
        "Hosting Facility": hosting_facility
    }

# Main script execution
if __name__ == "__main__":
    # Step 1: Fetch event links
    # base_url = "https://pickleballbrackets.com/pts.aspx"
    # fetch_event_links(base_url)

    # Step 2: Scrape data for each event and store in DataFrame
    event_data = []
    with open('event_links_200.txt', 'r') as file:
        event_links = [line.strip() for line in file.readlines()]
    
    for link in event_links:
        data = scrape_event_data(link)
        if data:
            event_data.append(data)
            print(f"Data fetched for URL {link}: {data}")

    # Step 3: Save data to Excel
    df = pd.DataFrame(event_data)
    df.to_excel("event_details_250.xlsx", index=False)
    print("Data successfully written to event_details.xlsx.")
