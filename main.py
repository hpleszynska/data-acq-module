from bs4 import BeautifulSoup
import re
import csv
from datetime import datetime

# Function to clean HTML content and extract raw text
def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    # Use space as a separator to maintain readability
    text = soup.get_text(separator=' ', strip=True)
    return text

# Function to extract reason and sequence of actions from the text content
def extract_reason_sequence(text_content):
    reason_pattern = re.compile(r'\b(due to|caused by|because of|result of|led to)\b\s+([^.]+)')
    sequence_pattern = re.compile(r'\b(before the accident|leading up to|prior to|just before)\b\s+([^.]+)')
    reason_matches = reason_pattern.findall(text_content)
    sequence_matches = sequence_pattern.findall(text_content)
    reason = '. '.join([' '.join(match) for match in reason_matches])
    sequence_of_actions = '. '.join([' '.join(match) for match in sequence_matches])
    return reason, sequence_of_actions

# Function to process the description and extract key information
def process_description(description):
    text_content = clean_html(description)
    # Regular expressions for vehicles, casualties, and injured persons
    vehicles_pattern = re.compile(r'\b(truck|autorickshaw|bus|motorcycle|SUV|car)\b', re.IGNORECASE)
    casualties_pattern = re.compile(r'(\d+)\s+(people|person|passengers)\s+(were\s+)?killed', re.IGNORECASE)
    injured_pattern = re.compile(r'(\d+)\s+(people|person|passengers)\s+(were\s+)?injured', re.IGNORECASE)
    # Find all matches and deduplicate vehicle types
    vehicles_involved = ', '.join(set(vehicles_pattern.findall(text_content)))
    # Search for casualties and injured persons
    casualties_match = casualties_pattern.search(text_content)
    casualties = casualties_match.group(1) if casualties_match else "0"
    injured_match = injured_pattern.search(text_content)
    injured = injured_match.group(1) if injured_match else "0"
    # Extract reason and sequence of actions
    reason, sequence_of_actions = extract_reason_sequence(text_content)
    return vehicles_involved, casualties, injured, reason, sequence_of_actions

# Function to extract article details from a given URL
def scrape_article_details(article_content):
    article_details = process_description(article_content)
    return article_details

# Main function to process CSV data and extract information
def process_csv_data(csv_file_path, output_csv_file):
    csv_columns = ['title', 'link', 'vehicles_involved', 'casualties', 'injured', 'reason', 'sequence_of_actions']
    processed_data = []
    # Read the CSV file containing article metadata and raw HTML text
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Use the raw HTML text for scraping article details
            article_details = scrape_article_details(row['raw text'])
            # Combine article metadata with extracted details
            processed_row = {
                'title': row['title'],
                'link': row['link'],
                'vehicles_involved': article_details[0],
                'casualties': article_details[1],
                'injured': article_details[2],
                'reason': article_details[3],
                'sequence_of_actions': article_details[4]
            }
            processed_data.append(processed_row)
    # Write the processed data to a new CSV file
    try:
        with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in processed_data:
                writer.writerow(data)
    except IOError as e:
        print(f"I/O error while writing to CSV: {e}")

# Example function call (uncomment to run)
# process_csv_data('input_csv_file.csv', 'processed_accidents_data.csv')

























# from bs4 import BeautifulSoup
# import requests
# import re
# import csv
#
#
# def clean_html(html_content):
#     soup = BeautifulSoup(html_content, 'html.parser')
#     text = soup.get_text(separator=' ', strip=True)
#     return text
#
#
# def extract_reason_sequence(text_content):
#     reason_pattern = re.compile(r'\b(due to|caused by|because of|result of|led to)\b\s+([^.]+)')
#     sequence_pattern = re.compile(r'\b(before the accident|leading up to|prior to|just before)\b\s+([^.]+)')
#
#     reason_matches = reason_pattern.findall(text_content)
#     sequence_matches = sequence_pattern.findall(text_content)
#
#     reason = '. '.join([' '.join(match) for match in reason_matches])
#     sequence_of_actions = '. '.join([' '.join(match) for match in sequence_matches])
#
#     return reason, sequence_of_actions
#
#
# def process_description(description):
#     text_content = clean_html(description)
#
#     vehicles_pattern = re.compile(r'\b(truck|autorickshaw|bus|motorcycle|SUV|car)\b', re.IGNORECASE)
#     casualties_pattern = re.compile(r'(\d+)\s+(people|person|passengers)\s+(were\s+)?killed', re.IGNORECASE)
#     injured_pattern = re.compile(r'(\d+)\s+(people|person|passengers)\s+(were\s+)?injured', re.IGNORECASE)
#
#     vehicles_involved = ', '.join(set(vehicles_pattern.findall(text_content)))
#
#     casualties_match = casualties_pattern.search(text_content)
#     casualties = casualties_match.group(1) if casualties_match else "0"
#
#     injured_match = injured_pattern.search(text_content)
#     injured = injured_match.group(1) if injured_match else "0"
#
#     reason, sequence_of_actions = extract_reason_sequence(text_content)
#
#     return vehicles_involved, casualties, injured, reason, sequence_of_actions
#
#
# def scrape_article_details(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         article_details = process_description(response.content)
#         return article_details
#     else:
#         print(f"Failed to retrieve the article page. Status code: {response.status_code}")
#         return None
#
#
# def scrape_news(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         news_blocks = soup.find_all('div', class_='news-block-four')
#         accidents_data = []
#
#         for block in news_blocks:
#             headline = block.find('h3').get_text().strip()
#             article_url = block.find('a', href=True)['href']
#             article_details = scrape_article_details(article_url)
#
#             if article_details:
#                 vehicles_involved, casualties, injured, reason, sequence_of_actions = article_details
#                 accidents_data.append({
#                     'title': headline,
#                     'link': article_url,
#                     'vehicles_involved': vehicles_involved,
#                     'casualties': casualties,
#                     'injured': injured,
#                     'reason': reason,
#                     'sequence_of_actions': sequence_of_actions
#                 })
#
#         csv_columns = ['title', 'link', 'vehicles_involved', 'casualties', 'injured', 'reason', 'sequence_of_actions']
#         csv_file = "AccidentsData.csv"
#
#         try:
#             with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
#                 writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#                 writer.writeheader()
#                 for accident in accidents_data:
#                     writer.writerow(accident)
#         except IOError:
#             print("I/O error")
#     else:
#         print(f"Failed to retrieve the main news page. Status code: {response.status_code}")
#
#
# url = 'https://www.unb.com.bd/news/tag/54'
# scrape_news(url)
#
#
#
#
#








# from bs4 import BeautifulSoup
# import requests
# import re
# import csv
# from datetime import datetime
#
# # Function to process and extract data from the description
# def process_description(description, title):
#     # Find location. Assuming it's in the title or the first sentence of the description.
#     location = title.split(" in ")[-1] if " in " in title else "Not specified"
#
#     # Find the date and time. Assuming a format like "Thursday (February 15, 2024) morning"
#     date_time_pattern = re.compile(r'on (\w+\s\(\w+\s\d{1,2},\s\d{4}\)\s\w+)')
#     date_time_match = date_time_pattern.search(description)
#     time = date_time_match.group(1) if date_time_match else "Not specified"
#
#     # Try to convert the time to a datetime object for consistency
#     try:
#         time = datetime.strptime(time, "%A (%B %d, %Y) %I:%M %p").strftime("%Y-%m-%d %H:%M:%S")
#     except ValueError:
#         # If the conversion fails, keep the original string
#         pass
#
#     # Find the vehicles involved. This is a simplistic approach and may need to be refined.
#     vehicles_pattern = re.compile(r'(\btruck\b|\bautorickshaw\b|\bbus\b|\bmotorcycle\b)', re.IGNORECASE)
#     vehicles_involved = vehicles_pattern.findall(description)
#
#     # Find casualties and injured
#     casualties_pattern = re.compile(r'(\d+)\s+(?:people|person|passengers)\s+(?:were\s+)?killed')
#     casualties_match = casualties_pattern.search(description)
#     casualties = casualties_match.group(1) if casualties_match else "0"
#
#     injured_pattern = re.compile(r'(\d+)\s+(?:people|person|passengers)\s+(?:were\s+)?injured')
#     injured_match = injured_pattern.search(description)
#     injured = injured_match.group(1) if injured_match else "0"
#
#     # Find ages (this will find all the ages mentioned, further logic needed to associate with casualties or injured)
#     ages_pattern = re.compile(r'(\d+)\s+(?:year|years)\s+old')
#     ages = ages_pattern.findall(description)
#
#     # Reason and sequence of actions would require more advanced NLP parsing
#     # For this example, we'll just copy the description
#     reason = description
#     sequence_of_actions = description
#
#     return location, time, vehicles_involved, casualties, injured, ages, reason, sequence_of_actions
#
#
# # URL of the webpage to scrape
# url = 'https://www.unb.com.bd/news/tag/54'
#
# # Make a request to get the HTML content of the page
# response = requests.get(url)
#
# # Check if the request was successful
# if response.status_code == 200:
#     soup = BeautifulSoup(response.content, 'html.parser')
# else:
#     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
#     soup = None
#
# # Placeholder list to store extracted data
# accidents_data = []
#
# if soup:
#     # Find all news blocks
#     news_blocks = soup.find_all('div', class_='news-block-four')
#
#     for block in news_blocks:
#         # Extract the headline
#         headline = block.find('h3').get_text().strip()
#
#         # Extract the link to the full article
#         link = block.find('a', href=True)['href']
#
#         # Extract the short description
#         description = block.find('div', class_='text').get_text().strip()
#
#         # Process the description to extract additional information
#         location, time, vehicles_involved, casualties, injured, ages, reason, sequence_of_actions = process_description(description, headline)
#
#         # Add the extracted data to our list
#         accidents_data.append({
#             'title': headline,
#             'link': link,
#             'description': description,
#             'location': location,
#             'time': time,
#             'vehicles_involved': vehicles_involved,
#             'casualties': casualties,
#             'injured': injured,
#             'ages': ages,
#             'reason': reason,
#             'sequence_of_actions': sequence_of_actions,
#         })
#
# # Write the extracted data to a CSV file
# csv_columns = ['title', 'link', 'description', 'location', 'time', 'vehicles_involved', 'casualties', 'injured', 'ages', 'reason', 'sequence_of_actions']
# csv_file = "AccidentsData.csv"
#
# try:
#     with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
#         writer.writeheader()
#         for accident in accidents_data:
#             writer.writerow(accident)
# except IOError:
#     print("I/O error")
#


























# from bs4 import BeautifulSoup
# import requests
# import re
# from datetime import datetime
#
#
# # The URL of the webpage to scrape
# url = 'https://www.unb.com.bd/news/tag/54'
#
# # Make a request to get the HTML content of the page
# response = requests.get(url)
#
# # Check if the request was successful
# if response.status_code == 200:
#     # The request was successful, the content can be found in response.content
#     html_content = response.content
#     # You can now use BeautifulSoup or other methods to parse this content
#     # For example, to get a BeautifulSoup object:
#     soup = BeautifulSoup(html_content, 'html.parser')
# else:
#     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
#     html_content = None
#     soup = None
#
# # Let's assume 'html_content' contains the full HTML of the page with the news blocks.
# soup = BeautifulSoup(html_content, 'html.parser')
#
# # Find all news blocks
# news_blocks = soup.find_all('div', class_='news-block-four')
#
# # Placeholder list to store extracted data
# accidents_data = []
#
# for block in news_blocks:
#     # Extract the headline
#     headline = block.find('h3').get_text().strip()
#
#     # Extract the link to the full article
#     link = block.find('a', href=True)['href']
#
#     # Extract the short description
#     description = block.find('div', class_='text').get_text().strip()
#
#     # Extract other required information from the description using regular expressions or string manipulation
#     # ...
#
#     # Add the extracted data to our list
#     accidents_data.append({
#         'headline': headline,
#         'link': link,
#         'description': description,
#         # ... other extracted data
#     })

# The accidents_data list now contains dictionaries with the scraped data.
# You would then continue to process this data, clean it, and finally store it in a CSV file.


# import requests
# import pandas as pd
# from bs4 import BeautifulSoup
#
# # Define the URL for UNB's accident news
# url = "https://www.unb.com.bd/news/tag/54"
#
# # Send an HTTP request to fetch the webpage content
# response = requests.get(url)
#
# # Parse the HTML content using BeautifulSoup
# # Check if the request was successful
# if response.status_code == 200:
#     soup = BeautifulSoup(response.content, "html.parser")
# else:
#     print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
#     html_content = None
#     soup = None
#
# # Find all articles with the "accident" tag
# articles = soup.find_all("div", class_="news-block-four")
#
# # Initialize lists to store extracted data
# publication_dates = []
# update_dates = []
# locations = []
# titles = []
# html_texts = []
# raw_texts = []
#
# # Extract relevant information from each article
# for article in articles:
#     publication_date = article.find("span", class_="news-date").text.strip()
#     update_date = article.find("span", class_="news-update").text.strip()
#     location = article.find("div", class_="text truncate-4").text.strip()
#     title = article.find("h3").text.strip()
#     html_text = article.find("div", class_="content-box").decode_contents()
#     raw_text = article.find("div", class_="content-box").text.strip()
#
#     # Append data to respective lists
#     publication_dates.append(publication_date)
#     update_dates.append(update_date)
#     locations.append(location)
#     titles.append(title)
#     html_texts.append(html_text)
#     raw_texts.append(raw_text)
#
# # Create a DataFrame from the extracted data
# df = pd.DataFrame({
#     "Publication Date": publication_dates,
#     "Update Date": update_dates,
#     "Location": locations,
#     "Title": titles,
#     "HTML Text": html_texts,
#     "Raw Text": raw_texts
# })
#
# # Save the DataFrame to a CSV file
# df.to_csv("accident_articles.csv", index=False)
#
# print("Data acquisition completed. CSV file saved as 'accident_articles.csv'.")
