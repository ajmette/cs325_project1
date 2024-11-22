import pytest
import os
import shutil
from unittest.mock import MagicMock, patch
import matplotlib.pyplot as plt
from modules import SentimentAnalysis, Phi3Model, create_folder, Get_Reviews, Plot_Combined_Graph
from config import sentiments_folder_path, reviews_folder_path, test_folder_path

# Test SentimentAnalysis class
def test_sentiment_analysis():
    # Create an instance of SentimentAnalysis
    sentiment = SentimentAnalysis("Product A")

    # Initial counts should be zero
    assert sentiment.get_counts() == {"Positive": 0, "Negative": 0, "Neutral": 0}

    # Add sentiments
    sentiment.add_sentiment("positive")
    sentiment.add_sentiment("Positive")
    sentiment.add_sentiment("negative")
    sentiment.add_sentiment("neutral")

    # Verify counts
    assert sentiment.get_counts() == {"Positive": 2, "Negative": 1, "Neutral": 1}

# Test analyze_reviews method of Phi3Model
def test_analyze_reviews():
    create_folder(test_folder_path)
    # Create an instance of Phi3Model
    phi3 = Phi3Model(sentiments_folder_path=test_folder_path)

    # Mock the generate_response method
    phi3.generate_response = lambda prompt: "Positive"  # Replace with a lambda returning a fixed response
    # Test analyze_reviews with mock data
    reviews = ["Review 1", "Review 2"]
    file_name = 'Test'
    responses = phi3.analyze_reviews(reviews, file_name)

    # Verify responses
    assert responses == 'Positive\nPositive\n'

    os.remove(os.path.join(test_folder_path, f"sentiments_product{file_name}.txt"))



# Test Get_Reviews by checking file creation and content
@patch("modules.webdriver.Chrome")
@patch("modules.requests.get")
@patch("modules.create_folder")
def test_get_reviews(mock_create_folder, mock_requests_get, mock_webdriver):
    # Mock dependencies
    mock_create_folder.return_value = None
    
    # Mock the Chrome WebDriver
    mock_driver = MagicMock()
    mock_webdriver.return_value = mock_driver
    mock_driver.page_source = """
        <html>
            <span class="ux-textspans ux-textspans--BOLD">Sample Product Title</span>
            <a class="fdbk-detail-list__tabbed-btn fake-btn fake-btn--large fake-btn--secondary" href="/feedback"></a>
        </html>
    """
    
    # Mock requests.get for feedback pages
    mock_requests_get.return_value.content = """
        <html>
            <div class="tabs__content">
                <div class="tabs__panel">
                    <div class="fdbk-container__details__comment">Great product!</div>
                    <a class="pagination__next icon-link" href="/next_page"></a>
                </div>
            </div>
        </html>
    """

    # Second mock request for the "next page"
    mock_requests_get.side_effect = [
        MagicMock(content="""
            <html>
                <div class="tabs__content">
                    <div class="tabs__panel">
                        <div class="fdbk-container__details__comment">Great product!</div>
                        <a class="pagination__next icon-link" href="/next_page"></a>
                    </div>
                </div>
            </html>
        """),
        MagicMock(content="""
            <html>
                <div class="tabs__content">
                    <div class="tabs__panel">
                        <div class="fdbk-container__details__comment">Another review!</div>
                    </div>
                </div>
            </html>
        """)
    ]

    # Create a mock `urls.txt` file
    urls_file = "urls_TEST.txt"
    with open(urls_file, "w", encoding="utf-8") as f:
        f.write("http://example.com/product\n")

    # Call Get_Reviews
    Get_Reviews("urls_TEST.txt", test_folder_path)

    # Check that the output file was created and contains the expected content
    output_file = os.path.join(test_folder_path, "reviews_product1.txt")
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Clean up test files
    os.remove(urls_file)
    os.remove(output_file)
    os.rmdir(test_folder_path)

    expected_content = "Great product!\nAnother review!\n"
    assert content == expected_content


#def test_plot_combined_graph_data():
#    products = [
#        MockProduct("Product 1", 10, 5, 3),
#        MockProduct("Product 2", 20, 7, 6),
#        MockProduct("Product 3", 15, 10, 4),
#    ]
#    result = Plot_Combined_Graph(products, return_data=True)
#
#    assert result["product_names"] == ["Product 1", "Product 2", "Product 3"]
#    assert result["positive_counts"] == [10, 20, 15]
#    assert result["negative_counts"] == [5, 7, 10]
#    assert result["neutral_counts"] == [3, 6, 4]

@pytest.mark.mpl_image_compare
def test_plot_combined_graph():
    class MockProduct:
            def __init__(self, name, positive, negative, neutral):
                self.product_name = name
                self.positive = positive
                self.negative = negative
                self.neutral = neutral

            def get_counts(self):
                return {
                    "Positive": self.positive,
                    "Negative": self.negative,
                    "Neutral": self.neutral
                }
    products = [
        MockProduct("Product 1", 10, 5, 3),
        MockProduct("Product 2", 20, 7, 6),
        MockProduct("Product 3", 15, 10, 4),
    ]
    Plot_Combined_Graph(products)
    #plt.close(fig)




#def test_delete():
#    if os.path.exists(test_folder_path):
#        print(f"Folder '{test_folder_path}' exists. Deleting...")
#        shutil.rmtree(test_folder_path)
#        print("Folder deleted.")
#    else:
#        print(f"Folder '{test_folder_path}' does not exist.")
