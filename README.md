#Product Review Scraper

##Libraries Used:

    1. beautifulsoup4 (used to scrape websites, pip install beautifulsoup4)

    2. requests (used for abstracting html, pip install requests)

    3. selenium (used for abstracting html when dynamic, pip install selenium)


##How to use review scraper:

    1. make sure to have Conda installed and working

    2. download the requirements.yaml file

    3. run command "conda env create -f requirements.yaml" to create a conda evironment with the needed requirements

    4. download urls.txt and scrappingProgram.py files

    5. run scrappingProgram.py inside the environment

    6. an output file (reviews_product<#>.txt) will be created for each product's reviews

    7. to add or change which ebay products are scraped, either add or replace ebay urls in urls.txt (each url needs to be on a new line)


##What this program does:

    This program takes an input text file of ebay urls. It scrapes those urls for all the products' reviews by going to the "See all feedback" page and looping through all the review pages. The reviews are then written to output files (separate output file for each url/product provided).