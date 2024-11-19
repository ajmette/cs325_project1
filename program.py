import ollama
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
import numpy as np

# ----------------- CHANGE TO OWN FOLDER PATHS, FOLDER EITHER DOESN'T ALREADY EXIST OR NEEDS TO BE EMPTY -----------------
reviews_folder_path = "C:/Users/ajmet/OneDrive/Desktop/CS325/project3/review/"
sentiments_folder_path = "C:/Users/ajmet/OneDrive/Desktop/CS325/project3/sentiment/"

def create_folder(path): # Creates the above folders if they don't already exists
    if not os.path.exists(path):
        os.makedirs(path)

class SentimentAnalysis:
    def __init__(self, product_name): # Stores the count for each sentiment
        self.product_name = product_name
        self.positive = 0
        self.negative = 0
        self.neutral = 0

    def add_sentiment(self, sentiment): # Increment the sentiment count based on the input
        if sentiment.lower() == "positive":
            self.positive += 1
        elif sentiment.lower() == "negative":
            self.negative += 1
        elif sentiment.lower() == "neutral":
            self.neutral += 1

    def get_counts(self):                                       # Return sentiment counts as a dictionary for testing purposes
        return {
            "Positive": self.positive,
            "Negative": self.negative,
            "Neutral": self.neutral
        }


def Get_Reviews():
    create_folder(reviews_folder_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")                   # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")                 # Optional: Required for certain Linux setups
    chrome_options.add_argument("--disable-dev-shm-usage")      # Optional: Helps with memory issues

    with open("urls.txt", 'r', encoding="utf-8") as input:      # Read product urls from txt file                     
        urls = input.readlines()

    input.close()

    count = 1                                                   # Used to name output files

    for url in urls:
        driver = webdriver.Chrome(options=chrome_options)       # Use selenium webdriver to get HTML from given url since the url isn't static
        driver.get(url)

        html = driver.page_source                               # Get the page source after all JavaScript has loaded
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')               # Parse the HTML to make easier to extract the user reviews
        
        title = soup.find('span', class_ = "ux-textspans ux-textspans--BOLD")
        
                                                                # Creates instance of class where product_name is the first 3 words of the product title + number
        sentiment = SentimentAnalysis(get_first_words(title.get_text(),3) + " #" + str(count))
        product_instances.append(sentiment)                     # Add sentiment data to product_instances
                                                                # Finds "See all feedback" button on product page
        all_page = soup.find('a', class_ = "fdbk-detail-list__tabbed-btn fake-btn fake-btn--large fake-btn--secondary")
        
        r = requests.get(str(all_page['href']))                 # Uses "href" url associated with "See all feedback" button to parse the html for all the reviews
        soup = BeautifulSoup(r.content, 'html.parser')
        
        reviews = ""                                            # Empty string that will be used to store reviews
        
        tabs = soup.find('div', class_ = "tabs__content")       # Finds all reviews on the current page of reviews
        cur_page = tabs.find('div', class_ = "tabs__panel")
        rws = cur_page.find_all('div', class_ = "fdbk-container__details__comment")
        
        for r in rws:                                           # Loops through reviews and adds them to string
            reviews += r.get_text() + "\n"

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
                reviews += r.get_text() + "\n"

                                                                # Finds "Next page" button (if no next page -> next_page = None)
            next_page = cur_page.find('a', class_ = "pagination__next icon-link")

                                                                # Open output file and write all reviews to it
        with open(reviews_folder_path + "reviews_product" + str(count)+".txt", "w", encoding="utf-8") as output:
                    output.write(reviews)

        output.close()
        count += 1                                              # Increment for next output filename


def get_first_words(s, num_words):
    words = s.split()                                           # Split the string into a list of words
    return ' '.join(words[:num_words])                          # Join the first `num_words` words back into a string


def Get_Sentiments(file_path, product_name, product_instances):
    create_folder(sentiments_folder_path)

    with open(file_path, 'r', encoding="utf-8") as file:        # Reads all reviews from text file
        reviews = file.readlines()
    file.close()

    for review in reviews:
        response = ollama.chat(                                 # Gets a Positive, Negative, or Neutral sentiment response for each review from phi3
            model='phi3',   
            messages=[{
                'role': 'user',
                'content': (f"Please rate the following review as Negative, Positive, or Neutral: {review}. Please only respond with a single word.")
            }],
            stream=True,
            options={                                           # Only allows certain number of tokens (num_predict) and turns down randomness of phi3's response (temperature)
                "num_predict": 3,
                "temperature": 0
            }
        )

        for chunk in response:                                  # Loops for each chunk of the response as the response comes in (since stream=True)
            with open(sentiments_folder_path + "sentiments_product" + str(count)+ ".txt", "a",  encoding="utf-8") as output:
                output.write(chunk['message']['content'])       # Writes the phi3 response to sentiments_product<#>.txt file

        with open(sentiments_folder_path + "sentiments_product" + str(count)+ ".txt", 'a') as output:
            output.write('\n')

    output.close()

    with open(sentiments_folder_path + "sentiments_product" + str(count)+ ".txt", 'r', encoding="utf-8") as reading:
        lines = reading.readlines()
    reading.close()

    sentiment = product_instances[find_instance_by_value(product_instances, product_name)]

    for line in lines:                                          # Count each category of sentiment
        if 'positive' in line.lower():
            sentiment.add_sentiment("positive")
        elif 'negative' in line.lower():
            sentiment.add_sentiment("negative")
        elif 'neutral' in line.lower():
            sentiment.add_sentiment("neutral")

    counts = sentiment.get_counts()
    print(f"Product: {product_name}\nCounts: {counts}")


def find_instance_by_value(instances, target_value):
    for i, instance in enumerate(instances):
        if instance.product_name == target_value:
            return i                                            # Returns the index of the instance
    return None                                                 # Return None if no match is found


def Plot_Combined_Graph(product_instances):
    total_products = len(product_instances)                     # Define the number of products
    
    fig, ax = plt.subplots(figsize=(10, 6))                     # Set up figure and axes

    bar_width = 0.25                                            # Define bar width and positions for each sentiment category
    index = np.arange(total_products)

    colors = ['red', 'blue', 'yellow']
    
    pos_counts = []                                             # Initialize empty lists to hold the sentiment data for each sentiment category
    neg_counts = []
    neutral_counts = []

    for product in product_instances:                           # Collect sentiment data for each product
        counts = product.get_counts()
        pos_counts.append(counts["Positive"])
        neg_counts.append(counts["Negative"])
        neutral_counts.append(counts["Neutral"])

                                                                # Create bars for each sentiment category for all products
    ax.bar(index - bar_width, neg_counts, bar_width, label="Negative", color=colors[0])
    ax.bar(index, pos_counts, bar_width, label="Positive", color=colors[1])
    ax.bar(index + bar_width, neutral_counts, bar_width, label="Neutral", color=colors[2])

    ax.set_xlabel("Products")                                   # Adding labels and title
    ax.set_ylabel("Number of Reviews")
    ax.set_title("Sentiment Analysis Across Multiple Products")
    ax.set_xticks(index)
    ax.set_xticklabels([product.product_name for product in product_instances])
    ax.legend(title="Sentiments")

    plt.tight_layout()                                          # Adding labels and title
    plt.show()



product_instances = []                                          # Array to hold instances of SentimentAnalysis class
Get_Reviews()
count = 1

for filename in os.listdir(reviews_folder_path):                # Get sentiments for all reviews of each file in the reviews folder
    file_path = os.path.join(reviews_folder_path, filename)
    if os.path.isfile(file_path):
        product_name = (product_instances[count - 1]).product_name
        Get_Sentiments(file_path, product_name, product_instances)
        count += 1

Plot_Combined_Graph(product_instances)                          # Graph all products' sentiments