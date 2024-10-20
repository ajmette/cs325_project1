import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Set Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Optional: Required for certain Linux setups
chrome_options.add_argument("--disable-dev-shm-usage")  # Optional: Helps with memory issues

with open("urls.txt", 'r') as input:         
    urls = input.readlines()

count = 0
for url in urls:

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Get the page source after all JavaScript has loaded
    html = driver.page_source

    #r = requests.get(url)
    soup = BeautifulSoup(html, 'html.parser')
    #feedback1 = soup.find('div', class_ = "d-stores-info-categories__details-container")
    #feedback = feedback1.find('div', class_ = "tabs__content")
    #fb = feedback.find('div', class_ = "tabs__cell")
    #print (soup.prettify())
    
    all_page = soup.find('a', class_ = "fdbk-detail-list__tabbed-btn fake-btn fake-btn--large fake-btn--secondary")
    print(all_page['href'])
    r = requests.get(str(all_page['href']))
    soup = BeautifulSoup(r.content, 'html.parser')

    #ul = soup.find('ul', {'class': 'fdbk-detail-list__cards'})
    t="" 
    
    tabs = soup.find('div', class_ = "tabs__content")
    cur_page = tabs.find('div', class_ = "tabs__panel")
    rws = cur_page.find_all('div', class_ = "fdbk-container__details__comment")
    for r in rws:
        t += r.get_text() + "\n\n"
    next_page = cur_page.find('a', class_ = "pagination__next icon-link")
    #print(str(count) + ": " )

    while (next_page != None): 
        #print("1 ")
        next_url = "https://www.ebay.com/fdbk/mweb_profile" + next_page['href']
        r = requests.get(next_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        tabs = soup.find('div', class_ = "tabs__content")
        cur_page = tabs.find('div', class_ = "tabs__panel")
        next_page = cur_page.find('a', class_ = "pagination__next icon-link")
        rws = cur_page.find_all('div', class_ = "fdbk-container__details__comment")
        for r in rws:
            t += r.get_text() + "\n\n"


    with open("reviews" + str(count)+".txt", "w", encoding="utf-8") as reviews:
                reviews.write(t)
    count +=1
    #print("done\n")
    
    '''if ul:
        with open("reviews" +str(count)+".txt", "w", encoding="utf-8") as reviews:  
            for elem in ul.find_all(class_ = "fdbk-container__details__comment"):   
                reviews.write(elem.get_text() + "\n\n") 

        
    else:
        print(f"No 'ul' element found for {url}")'''
