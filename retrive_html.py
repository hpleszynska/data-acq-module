import requests
from bs4 import BeautifulSoup
import time
import csv
from datetime import datetime

def parse_datetime(date_string):
    if date_string == "NA":
        return date_string
    date_format = "%B %d, %Y, %I:%M %p"
    parsed_datetime = datetime.strptime(date_string, date_format)
    formatted_date = parsed_datetime.strftime('%Y%m%d')
    return formatted_date
def remove_links_text(html_text):
    raw_text = html_text
    for a_tag in soup.find_all('a'):
        raw_text = raw_text.replace(a_tag.get_text(), '')
    return raw_text
def html_to_raw_text(html):
    raw_text = html.text
    for a_tag in html.find_all('a'):
        raw_text = raw_text.replace(a_tag.get_text(), '')
    return raw_text.strip().replace('\n', '')

# def extract_raw_text(html_text):
#     soup = BeautifulSoup(html_text, 'html.parser')
#     for element in soup.find_all(['a', 'script']):
#         element.extract()
#     raw_text = soup.get_text(separator='', strip=True)
#     return raw_text
def remove_classes_and_styles(html):
    for tag in html.find_all(True):
        if 'class' in tag.attrs:
            del tag['class']
        if 'style' in tag.attrs:
            del tag['style']
    return html
def write_to_csv(data_list, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        for data_row in data_list:
            wrapped_data_row = ["<{}>".format(item) for item in data_row]
            writer.writerow(wrapped_data_row)

def extract_date(line):
    date_string = line
    if "-" in line:
        date_string = line.split("-", 1)[1].strip()
    return date_string

def process_links(unique_links):
    for link in list(unique_links)[:20]: 
        response = requests.get(link)
        if response.status_code == 200:
            page_soup = BeautifulSoup(response.content, 'html.parser')
            body = page_soup.find('body')
            page_wrapper = body.find('div', class_='page-wrapper')
            main = page_wrapper.find('main')
            page_container = main.find('div', class_='sidebar-page-container news-details')
            row_clearfix = page_container.find('div', class_='row clearfix')
            content_side = row_clearfix.find('div', class_='content-side col-lg-8 col-md-8 col-sm-12 col-xs-12')
            content = content_side.find('div', class_='content')
            blong_single_post = content.find('div', class_='blog-single news-details')
            html_text = content.find('div', class_='text').text
            html= content.find('div', class_='text')
            inner_box = blong_single_post.find('div', class_='inner-box')
            upper_box = inner_box.find('div', class_='upper-box')
            #details_list = upper_box.find('ul', class_='post-meta hidden-sm hidden-md hidden-lg')
            details_hidden_list = upper_box.find('ul', class_='post-meta hidden-xs')
            list_items = details_hidden_list.find_all('li')
            location = list_items[1].text
            publication_date = list_items[2].text
            if len(list_items) >= 5:
                update_date = list_items[4].text
            else:
                update_date = "NA"
            if len(list_items)<5:
                continue
            title = upper_box.find('h2').text
            publication_date = parse_datetime(extract_date(publication_date.strip()))
            update_date = parse_datetime(extract_date(update_date.strip()))
            raw_text = html_to_raw_text(html)
            html= remove_classes_and_styles(html)
            data_list = [[publication_date, update_date, location, title, html, raw_text]]
            filename = "output.csv"
            write_to_csv(data_list, filename)
            
        else:
            print("Failed to navigate to:", link)


#for loop that fetches posts from the UNB website
#The loop will fetch 400 pages of posts 
for i in range(1, 400):
    url = "https://unb.com.bd/api/tag-news?tag_id=54&item=%d" % (i)
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        html_content = json_data.get('html')
        if html_content:
            soup = BeautifulSoup(html_content, 'html.parser')
            links = soup.find_all('a')
            unique_links = set()
            for link in links[:20]:
                href = link.get('href')
                if href:
                    link_response = requests.get(href)
                    if link_response.status_code == 200:
                        unique_links.add(href)
                    else:
                        print("Failed to navigate to:", href)
            process_links(unique_links)
            time.sleep(10)
        else:
            print("No HTML content found in the JSON response.")
    else:
        print("Failed to fetch data: ", response.status_code)