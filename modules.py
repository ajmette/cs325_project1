import ollama
import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import matplotlib.pyplot as plt
import numpy as np
from abc import ABC, abstractmethod
from config import reviews_folder_path, sentiments_folder_path, product_instances, count


class LM_Interface(ABC):
    @abstractmethod
    def generate_response(self, prompt: str) -> str: # Generate a response from the language model
        pass


class Phi3Model(LM_Interface):
    def __init__(self, sentiments_folder_path: str):
        self.sentiments_folder_path = sentiments_folder_path

    def generate_response(self, prompt: str) -> str:            # Generate a response from phi3 for a single prompt
        response = ollama.chat(
            model='phi3',
            messages=[{
                'role': 'user',
                'content': prompt
            }],
            stream=True,
            options={
                "num_predict": 3,
                "temperature": 0
            }
        )

        full_response = ""
        for chunk in response:
            full_response += chunk['message']['content']
        return full_response

    def analyze_reviews(self, reviews: list[str], count) -> None: # Analyzes a list of reviews and writes sentiment analysis results to text files.

        responses = ""

        for review in reviews:
            
            prompt = (
                f"Please rate the following review as Negative, Positive, or Neutral: {review}. "
                "Please only respond with a single word."
            )
            
            responses += self.generate_response(prompt) + "\n"  # Generate response using phi3 using above prompt

            
        with open(os.path.join(self.sentiments_folder_path, f"sentiments_product{count}.txt"), "w", encoding="utf-8") as output:
            output.write(responses)                             # Write the response to file and add a newline

        return responses


def create_folder(path):                                        # Creates the folders if they don't already exists
    if not os.path.exists(path):
        os.makedirs(path)

class SentimentAnalysis:
    def __init__(self, product_name):                           # Stores the count for each sentiment
        self.product_name = product_name
        self.positive = 0
        self.negative = 0
        self.neutral = 0

    def add_sentiment(self, sentiment):                         # Increment the sentiment count based on the input
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


def Get_Reviews(file, reviews_folder_path):
    create_folder(reviews_folder_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")                   # Run Chrome in headless mode
    chrome_options.add_argument("--no-sandbox")                 # Optional: Required for certain Linux setups
    chrome_options.add_argument("--disable-dev-shm-usage")      # Optional: Helps with memory issues

    with open(file, 'r', encoding="utf-8") as input:            # Read product urls from txt file                     
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
        sentiment = SentimentAnalysis("#" + str(count) + ": " + get_first_words(title.get_text(),3))
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
        with open(os.path.join(reviews_folder_path, f"reviews_product{count}.txt"), "w", encoding="utf-8") as output:
                    output.write(reviews)

        output.close()
        count += 1                                              # Increment for next output filename


def get_first_words(s, num_words):
    words = s.split()                                           # Split the string into a list of words
    return ' '.join(words[:num_words])                          # Join the first `num_words` words back into a string


def Get_Sentiments(file_path, product_name, product_instances, count):
    create_folder(sentiments_folder_path)
    
    with open(file_path, 'r', encoding="utf-8") as file:        # Reads all reviews from text file
        reviews_read = file.readlines()
    file.close()

    phi3 = Phi3Model(sentiments_folder_path)                    # Initialize Phi3Model with the folder path for sentiment files

    responses = phi3.analyze_reviews(reviews_read, count)       # Perform sentiment analysis and save results to files

    with open(os.path.join(sentiments_folder_path, f"sentiments_product{count}.txt"), 'r', encoding="utf-8") as reading:
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