import requests
from bs4 import BeautifulSoup

with open("urls.txt", 'r') as input:         
    urls = input.readlines()

count = 0
for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    #ul = soup.find('ul', {'class': 'fdbk-detail-list__cards'})
    t="" 
    
    tabs = soup.find('div', class_ = "tabs__content")
    cur = tabs.find('div', class_ = "tabs__panel")
    rws = cur.find_all('div', class_ = "fdbk-container__details__comment")
    for r in rws:
        t += r.get_text() + "\n\n"
    next = cur.find('a', class_ = "pagination__next icon-link")
    #print(str(count) + ": " )

    while (next != None): 
        #print("1 ")
        next_url = "https://www.ebay.com/fdbk/mweb_profile" + next['href']
        r = requests.get(next_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        tabs = soup.find('div', class_ = "tabs__content")
        cur = tabs.find('div', class_ = "tabs__panel")
        next = cur.find('a', class_ = "pagination__next icon-link")
        rws = cur.find_all('div', class_ = "fdbk-container__details__comment")
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
