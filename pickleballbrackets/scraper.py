from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Function to set up the WebDriver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Optional: run headless
    options.add_argument('--log-level=3')  # Suppress all logging

    # Setting the logging preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,  # Disable notifications
        "safebrowsing.enabled": "true"  # Enable Safe Browsing
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Function to fetch information from a link
def fetch_info_from_link(link):
    driver = setup_driver()

    # Navigate to the website
    driver.get(link)
    time.sleep(5)  # Allow time for the JavaScript to render

    # Initialize variables to store the extracted data
    main_text = ""
    address = ""
    date_text = ""  # Initialize date_text
    additional_info = ""  # Initialize additional_info

    try:
        # Extracting specific text from the specified inner div
        main_div = driver.find_element(By.CLASS_NAME, 'flex.flex-col.justify-center.gap-4.transition-all.duration-300')
        inner_main_div = main_div.find_element(By.CLASS_NAME, 'hidden.flex-row.items-center.text-2xl.font-semibold.text-gray-900.sm\\:flex')
        main_text = inner_main_div.text  # Get text from the inner div

        # Fetch date text from the specified child div
        try:
            date_div = main_div.find_element(By.XPATH, './/div[contains(@class, "flex flex-row flex-wrap gap-4 sm:flex-nowrap")]//div[1]')  # Updated XPath
            date_text = date_div.text
        except Exception as e:
            print(f"Date element not found: {str(e)}")

        # Locating the container div with 3 inner divs for the address
        last_div_container = driver.find_element(By.CLASS_NAME, 'my-6.grid.grid-cols-1.gap-6.sm\\:grid-cols-2.lg\\:grid-cols-3')
        last_divs = last_div_container.find_elements(By.CLASS_NAME, 'flex.flex-col.gap-4.rounded-lg.bg-white.p-4')

        if last_divs and len(last_divs) >= 3:
            # Select the third (last) div
            third_div = last_divs[2]
            # Extract the address information specifically from the nested div
            address_div = third_div.find_element(By.CLASS_NAME, 'flex.w-full.flex-col.gap-2.text-gray-900')
            address = ", ".join([div.text for div in address_div.find_elements(By.TAG_NAME, 'div')])

        # Fetch additional info from the child div
        additional_info_div = main_div.find_element(By.CLASS_NAME, 'flex.flex-row.flex-wrap.gap-4.sm\\:flex-nowrap')
        additional_info = additional_info_div.text  # Get text from the child div

    except Exception as e:
        print(f"Error fetching info from {link}: {str(e)}")
    finally:
        driver.quit()

    return main_text, address, date_text, additional_info




def process_links():
    with open('tournament_links.txt', 'r') as file:
        links = [line.strip() for line in file.readlines()]

    # List to hold all fetched information for DataFrame creation
    all_info = []
    for link in links:
        main_text, address, date_text, additional_info = fetch_info_from_link(link)
        all_info.append({
            'Name of The Tournament': main_text,
            'Location': address,
            'Date': date_text,
            "Hosting Facility": "No Parking fee" 
        })
        print("Fetched information:")
        print(f"  Name of The Tournament: {main_text}")
        print(f"  Address: {address}")
        print(f"  Date: {date_text}")
        print(f"  Additional Info: {additional_info}\n")

    # Create a DataFrame and save to Excel
    df = pd.DataFrame(all_info)
    df.to_excel('tournament_info.xlsx', index=False)

    print("Data saved to tournament_info.xlsx")

# Run the function
if __name__ == "__main__":
    process_links()
