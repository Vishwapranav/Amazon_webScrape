from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

def scrape_amazon_products(search_query, num_pages, dropdown_choice):
    DRIVER_PATH = r'.\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(DRIVER_PATH)
    browser = webdriver.Chrome(service=service)
    browser.get('https://www.amazon.in')
    browser.maximize_window()
    
    # Perform the search
    input_search = browser.find_element(By.ID, 'twotabsearchtextbox')
    search_button = browser.find_element(By.XPATH, "(//input[@type='submit'])[1]")
    input_search.send_keys(search_query)
    sleep(1)
    search_button.click()
    
    # Handle dropdown selection
    try:
        button = browser.find_element(By.ID, "a-autoid-0-announce")
        button.click()
        wait(browser, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "a-dropdown-link")))
        dropdown_options = browser.find_elements(By.CLASS_NAME, "a-dropdown-link")
        
        # Check if user choice is valid
        if 0 <= dropdown_choice - 1 < len(dropdown_options):
            dropdown_options[dropdown_choice - 1].click()
            print(f"Selected dropdown option: {dropdown_options[dropdown_choice - 1].text.strip()}")
        else:
            print("Invalid dropdown choice.")
    except Exception as e:
        print("Dropdown selection error:", e)
    
    # Initialize data lists
    product_data = {
        "asin": [], "name": [], "price": [], "ratings": [], "ratings_count": [], "link": []
    }

    # Scrape data from each page
    for page in range(num_pages):
        print(f"Scraping page {page + 1}")
        
        items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
        
        for item in items:
            # Extract ASIN
            data_asin = item.get_attribute("data-asin")
            product_data["asin"].append(data_asin)
            
            # Extract name (checks both vertical and horizontal layouts)
            try:
                name = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]').text
            except:
                try:
                    name = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]').text
                except:
                    name = "N/A"
            product_data["name"].append(name)
            
            # Extract price
            try:
                whole_price = item.find_element(By.XPATH, './/span[@class="a-price-whole"]').text
            except:
                whole_price = "0"
            product_data["price"].append(whole_price)
            
            # Extract ratings and ratings count
            try:
                ratings_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')
                ratings = ratings_box[0].get_attribute('aria-label') if ratings_box else "0"
                ratings_count = ratings_box[1].get_attribute('aria-label') if len(ratings_box) > 1 else "0"
            except:
                ratings, ratings_count = "0", "0"
            product_data["ratings"].append(ratings)
            product_data["ratings_count"].append(ratings_count)
            
            # Extract link
            try:
                link = item.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")
            except:
                link = "N/A"
            product_data["link"].append(link)
        
        # Go to the next page if available
        try:
            next_button = browser.find_element(By.XPATH, "//a[text()='Next']")
            next_button.click()
            sleep(2)
        except:
            print("Next page not found.")
            break

    browser.quit()
    return product_data

# Get user input
# search_query = input("Enter search query: ")
# num_pages = int(input("Enter number of pages to scrape: "))
# dropdown_choice = int(input("Enter dropdown option number: "))

# # Call the function
# product_data = scrape_amazon_products(search_query, num_pages, dropdown_choice)
# print("Scraped Data:", product_data)
