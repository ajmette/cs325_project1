from modules import Get_Reviews, Get_Sentiments, Plot_Combined_Graph
import os
from config import reviews_folder_path, sentiments_folder_path, product_instances

if __name__ == "__main__":
    Get_Reviews("urls.txt", reviews_folder_path)

    count = 1
    #Get_Sentiments()
    for filename in os.listdir(reviews_folder_path):                # Get sentiments for all reviews of each file in the reviews folder
        file_path = os.path.join(reviews_folder_path, filename)
        if os.path.isfile(file_path):
            product_name = (product_instances[count - 1]).product_name
            Get_Sentiments(file_path, product_name, product_instances, count)
            count += 1

    Plot_Combined_Graph(product_instances)                          # Graph all products' sentiments