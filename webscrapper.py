import requests
from bs4 import BeautifulSoup
from autoscraper import AutoScraper

def scrape_data_from_tag(url, tag):
    # Send a GET request to the URL and retrieve the HTML content
    response = requests.get(url)
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the elements with the provided tag
        elements = soup.find_all(tag)
        
        # Extract the text content from the elements
        if tag == "img":
            data = [element['src'] for element in elements]
        else:
            data = [element.get_text() for element in elements]
        
        return data
    else:
        print(f"Failed to fetch data from {url}. Error code: {response.status_code}")
        return []


def scrape_data_from_wanted_list(url, wanted_list):
    scraper = AutoScraper()
    result = scraper.build(url, wanted_list)
    return result


# Example usage

user_url = input("Enter the URL you want to scrape: ")
user_input = input("Enter the HTML tag you want to scrape or the text you want to find: ")

if user_input.startswith("<") and user_input.endswith(">"):
    user_tag = user_input.lower() 
    user_tag =  user_tag[1:-1]
    scraped_data = scrape_data_from_tag(user_url, user_tag)
    print(scraped_data)
else:
    user_wanted_text = [user_input]  # Assume user input is wanted text
    scraped_data = scrape_data_from_wanted_list(user_url, user_wanted_text)
    print(scraped_data)




