from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

def scrape_amazon_details(search_query, num_pages, dropdown_choice):
    DRIVER_PATH = r'.\chromedriver-win64\chromedriver-win64\chromedriver.exe'
    service = Service(DRIVER_PATH)
    browser = webdriver.Chrome(service=service)
    browser.get('https://www.amazon.in')
    browser.maximize_window()
    
    # Perform search
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

    # Initialize lists to store scraped data
    desc_titles, desc_contents, product_links, reviews, features_list = [], [], [], [], []
    
    for i in range(num_pages):
        print(f"Scraping page {i + 1}")
        
        items = wait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
        
        # Clear product_links for each new page
        product_links.clear()

        for item in items:
            # Get product link
            link = item.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")
            product_links.append(link)

        # Scrape each product page
        for product_link in product_links:
            browser.get(product_link)
            sleep(2)
            
            # Scrape review summary
            try:
                product_summary = browser.find_element(By.ID, "product-summary")
                review_cont = product_summary.find_elements(By.CLASS_NAME, "a-spacing-small")[1]
                review = review_cont.find_element(By.TAG_NAME, 'span').text
            except:
                review = "NA"
            reviews.append(review)
            
            # Scrape 'About this item' section
            try:
                about_section = browser.find_element(By.ID, 'feature-bullets').find_elements(By.TAG_NAME, 'li')
                about_features = [bullet.find_element(By.TAG_NAME, 'span').text for bullet in about_section]
            except:
                about_features = ["NA"]
            features_list.append(about_features)
            
            # Scrape product description
            desc_content, desc_title = [], []
            try:
                tech_table = browser.find_element(By.ID, 'tech').find_elements(By.TAG_NAME, "tbody")
                for tbody in tech_table:
                    rows = tbody.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        col1 = row.find_elements(By.TAG_NAME, "td")[0].find_element(By.TAG_NAME, "p").find_element(By.TAG_NAME, "strong").text
                        col2 = row.find_elements(By.TAG_NAME, "td")[1].find_element(By.TAG_NAME, "p").text
                        desc_title.append(col1)
                        desc_content.append(col2)
            except:
                desc_title, desc_content = ["NA"], ["NA"]
            
            desc_titles.append(desc_title)
            desc_contents.append(desc_content)
            
            browser.back()
            sleep(1)
        
        # Go to the next page if available
        try:
            next_button = browser.find_element(By.XPATH, "//a[text()='Next']")
            next_button.click()
            sleep(2)
        except:
            print("No more pages available.")
            break
    
    browser.quit()
    
    # Return data as a dictionary
    return {
        "product_links": product_links,
        "reviews": reviews,
        "features": features_list,
        "desc_titles": desc_titles,
        "desc_contents": desc_contents
    }

# Get user input
search_query = input("Enter search query: ")
num_pages = int(input("Enter number of pages to scrape: "))
dropdown_choice = int(input("Dropdown choice: "))

# Call the function and display results
product_data = scrape_amazon_details(search_query, num_pages, dropdown_choice)
print("Scraped Data:", product_data)
