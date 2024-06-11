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

def html_to_raw_text(html):
    raw_text = html.text
    for a_tag in html.find_all('a'):
        raw_text = raw_text.replace(a_tag.get_text(), '')
    return raw_text.strip().replace('\n', '')

def write_to_csv(data_list, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        for data_row in data_list:  
            writer.writerow(data_row)
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
            html= content.find('div', class_='text')
            inner_box = blong_single_post.find('div', class_='inner-box')
            upper_box = inner_box.find('div', class_='upper-box')
            details_hidden_list = upper_box.find('ul', class_='post-meta hidden-xs')
            list_items = details_hidden_list.find_all('li')
            categories = {}
            for item in list_items:
                span = item.find('span')  
                if span:
                    span_class = span.get('class')  
                    last_class = span_class[-1]                    
                    if 'Publish-' in item.text:
                        categories[last_class+'-p']=item.text
                    if 'Update-' in item.text:
                        categories[last_class+'-u']=item.text
                    else:
                        categories[last_class]=item.text
            location = categories.get('fa-map-marker', 'NA')
            publication_date = categories.get('qb-clock-p', 'NA')
            update_date = categories.get('qb-clock-u', 'NA')
            title = upper_box.find('h2').text
            publication_date = parse_datetime(extract_date(publication_date.strip()))
            update_date = parse_datetime(extract_date(update_date.strip()))
            raw_text = html_to_raw_text(html)
            data_list = [[publication_date, update_date, location, title,  html, raw_text]]
            filename = "output.csv"
            write_to_csv(data_list, filename)
            
        else:
            print("Failed to navigate to:", link)


for i in range(1, 10000):
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
                    if "https://unb.com.bd/category/World/" in href:
                        continue
                    else:
                        link_response = requests.get(href)
                        if link_response.status_code == 200:
                            unique_links.add(href)
                        else:
                            print("Failed to navigate to:", href)
            process_links(unique_links)
            time.sleep(5)
        else:
            print("No HTML content found in the JSON response.")
    else:
        print("Failed to fetch data: ", response.status_code)

print("end")