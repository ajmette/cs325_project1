## Libraries used:
- ollama (interact with SLM phi3)
- os (navigate file explorer)
- requests (abstract html)
- selenium (abstract html when dynamic or when website thinks program is a bot)
- BeautifulSoup4 (scrape websites)
- matplotlib (create graph)


## How to use:
1. make sure to have Conda installed and working
2. download the requirements.yaml file
3. run command "conda env create -f requirements.yaml" to create a conda evironment with the needed requirements
4. make sure Ollama phi3 is running
5. download urls.txt, program.py, modules.py, config.py files <br>
‼️ **Note:** Make sure to change `reviews_folder_path` and `sentiments_folder_path` in the `config.py` file
6. run program.py inside the environment
7. reviews_product<#>.txt files will be created (one for each of the links/products)
8. sentiments_product<#>.txt files will be created from each of the reviews_product<#>.txt files
9. an overall graph will be created to compare all of the sentiments_product<#>.txt files


## What this program does:
This program takes a single text file with ebay product urls as input. These urls are scraped for all of the reviews for that product. A reivew_product text file is created for each given product. Phi3 then gives a one word sentiment (positive, negative, or neutral) for each review in each of the files. These sentiments are stored in text files (again one file for each given product url). The program then creates a single graph comparing the counts of positive, negative, and neutral between each product. 

![combined graph of multiple products' sentiments](graph.png)