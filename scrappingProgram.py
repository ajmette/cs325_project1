import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options

                                                            # Set Chrome options, so then doesn't open Chrome browser
chrome_options = Options()
chrome_options.add_argument("--headless")                   # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")                 # Optional: Required for certain Linux setups
chrome_options.add_argument("--disable-dev-shm-usage")      # Optional: Helps with memory issues


with open("urls.txt", 'r') as input:                        # Read product urls from txt file                     
    urls = input.readlines()


count = 1                                                   # Used to name output files

for url in urls:
    driver = webdriver.Chrome(options=chrome_options)       # Use selenium webdriver to get HTML from given url since the url isn't static
    driver.get(url)

    html = driver.page_source                               # Get the page source after all JavaScript has loaded
    
    soup = BeautifulSoup(html, 'html.parser')               # Parse the HTML to make easier to extract the user reviews
    
                                                            # Finds "See all feedback" button on product page
    all_page = soup.find('a', class_ = "fdbk-detail-list__tabbed-btn fake-btn fake-btn--large fake-btn--secondary")
    
    r = requests.get(str(all_page['href']))                 # Uses "href" url associated with "See all feedback" button to parse the html for all the reviews
    soup = BeautifulSoup(r.content, 'html.parser')
    
    reviews = ""                                            # Empty string that will be used to store reviews
    
    tabs = soup.find('div', class_ = "tabs__content")       # Finds all reviews on the current page of reviews
    cur_page = tabs.find('div', class_ = "tabs__panel")
    rws = cur_page.find_all('div', class_ = "fdbk-container__details__comment")
    
    for r in rws:                                           # Loops through reviews and adds them to string
        reviews += r.get_text() + "\n\n"

                                                            # Finds "Next page" button (if no next page -> next_page = None)
    next_page = cur_page.find('a', class_ = "pagination__next icon-link")

    
    while (next_page != None):                              # Loop through all review pages until no more pages available
                                                            # Get url for the next page by using "href" associated with "Next page" button
        next_url = "https://www.ebay.com/fdbk/mweb_profile" + next_page['href']

        r = requests.get(next_url)                          # Parse html next_url, find all reviews, and add reviews to string
        soup = BeautifulSoup(r.content, 'html.parser')
        tabs = soup.find('div', class_ = "tabs__content")
        cur_page = tabs.find('div', class_ = "tabs__panel")
        rws = cur_page.find_all('div', class_ = "fdbk-container__details__comment")
        for r in rws:
            reviews += r.get_text() + "\n\n"

                                                            # Finds "Next page" button (if no next page -> next_page = None)
        next_page = cur_page.find('a', class_ = "pagination__next icon-link")

                                                            # Open output file and write all reviews to it
    with open("reviews_product" + str(count)+".txt", "w", encoding="utf-8") as output:
                output.write(reviews)

    count += 1                                              # Increment for next output filename


driver.quit()                                               # quit and close
output.close()
input.close()
