import requests
from bs4 import BeautifulSoup

with open("urls.txt", 'r') as input:         
    urls = input.readlines()

count = 0
for url in urls:
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    ul = soup.find('ul', {'class': 'fdbk-detail-list__cards'})

    if ul:
        with open("reviews" +str(count)+".txt", "w", encoding="utf-8") as reviews:  
            for elem in ul.find_all(class_ = "fdbk-container__details__comment"):   
                reviews.write(elem.get_text() + "\n\n") 

        count +=1
    else:
        print(f"No 'ul' element found for {url}")
