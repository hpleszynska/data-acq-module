import csv
import re
import nltk
import string
import requests
import logging
import openai
from nltk.corpus import stopwords

logging.basicConfig(filename='processing_log.log', level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(message)s')

openai.api_key = "-"
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')


def sum_numbers(*args):
    return sum(int(num) if num.isdigit() else 0 for num in args)

def validate_data(casualties, injured):
    if not casualties or not all(c.isdigit() or c == 'one' for c in casualties):
        logging.warning("Invalid or missing casualty data.")
    if not injured or not all(i.isdigit() or i == 'one' for i in injured):
        logging.warning("Invalid or missing injury data.")

def find_casualties(raw_text):
    text = nltk.sent_tokenize(raw_text)
    text = [nltk.word_tokenize(t) for t in text]
    words = []
    for t in text:
        help = []
        for i in t:
            if i not in nltk.corpus.stopwords.words('english') and i not in string.punctuation:
                help.append(i)
        if help.count('injured') > 0 or help.count('killed') > 0 or help.count('died') > 0: #eliminates sentences without one of those words
            words.append(help)

    text = [nltk.pos_tag(w) for w in words]

    grammar = r"""
    NP: {<DT|PP\$>?<JJ>*<NN>}
          {<CD>?<NNS|NNP>+}
    VNP: {<NP>?<VBD>}
        {<CD>?<VBD>}
    """
    cp = nltk.RegexpParser(grammar)
    text = [cp.parse(t) for t in text]

    injured = []
    killed = []

    for sent in text:
        for tree in sent:
            #for subtree in tree:
            if isinstance(tree, nltk.Tree):
                print(tree)
                if tree.label() == 'VNP':
                    check = 0
                    for leaf in tree.leaves():
                        #print(leaf)
                        if leaf[0] == 'died' or leaf[0] == 'killed':
                            check = 1
                            break
                        elif leaf[0] == 'injured':
                            check = 2
                            break
                    #print(check)
                    if check == 1:
                        for leaf in tree.leaves():
                            #print(leaf)
                            if leaf[1] == 'CD':
                                #print('killed appended')
                                killed.append(leaf[0])
                                number = 1
                                break
                        if len(killed) == 0:
                            killed.append('one')
                    elif check == 2:
                        for leaf in tree.leaves():
                            if leaf[1] == 'CD':
                                injured.append(leaf[0]) # ROBERTA
                                number = 1
                                break
                        if len(injured) == 0:
                            injured.append('one')
                    # if tree.leaves().count('died') > 0 or tree.leaves().count('killed') > 0:
                    #     killed.append(tree.leaves())
                    # elif tree.leaves().count('injured') > 0:
                    #     injured.append(tree.leaves())

    return killed, injured



def get_district_by_city(city_name, api_key):
    if not city_name or city_name == 'NA':
        logging.error("Invalid or empty city name provided.")
        return 'Unknown District'

    query = f"{city_name}, Bangladesh"
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': query,
        'key': api_key,
        'pretty': 1
    }

    logging.debug(f"Querying OpenCage API with: {query}")

    try:
        response = requests.get(base_url, params=params)
        logging.debug(f"API Response Status: {response.status_code}")
        logging.debug(f"API Response: {response.text}")  # Log the full response text for debugging

        if response.status_code == 200:
            data = response.json()
            if data['results']:
                components = data['results'][0]['components']
                district = components.get('state_district', components.get('county', 'Unknown District'))
                if district != 'Unknown District':
                    logging.info(f"District found: {district} for {city_name}.")
                    return district
                else:
                    logging.warning(f"No district found in API response for {city_name}. Using default 'Unknown District'.")
            else:
                logging.warning(f"No results found in API response for {city_name}. Returning 'Unknown District'.")
        else:
            logging.error(f"API response for {city_name} returned status code {response.status_code}. Returning 'Unknown District'.")
        return 'Unknown District'
    except requests.RequestException as e:
        logging.error(f"API request error for city {city_name}: {e}")
        return 'Unknown District'





api_key = '0fc1ca12558642099934e81ef732db09'


def process_raw_text(raw_text):
    try:
        lines = raw_text.split('\n')
        vehicles_pattern = re.compile(r'(trucks?|motorcycles?|autorickshaws?|buses?|cars?|SUVs?|microbuses?|trains?|microbus?)', re.IGNORECASE)
        vehicles_involved = {match.group(0).lower() for line in lines for match in vehicles_pattern.finditer(line)}
        casualties, injured = find_casualties(raw_text)

        #     # OpenAI API call
        # response = openai.Completion.create(
        #     engine="davinci",
        #     prompt=f"Extract the sequence of actions and the reason for the accident from the following text: {raw_text}",
        #     temperature=0.5,
        #     max_tokens=100,
        #     top_p=1.0,
        #     frequency_penalty=0.0,
        #     presence_penalty=0.0
        # )
        #
        # # Extract the sequence of actions and reason from the response
        # if response['choices']:
        #     extracted_text = response['choices'][0]['text'].strip()
        #     reason, sequence_of_actions = extracted_text.split('\n')
        validate_data(casualties, injured)
        vehicles_str = ', '.join(sorted(vehicles_involved))
        return vehicles_str, casualties, injured, '', ''
    except Exception as e:
        logging.error(f"Error in process_raw_text: {e}")
        return '', [], [], '', ''



def clean_city_name(location):
    clean_name = re.sub(r"<.*?>", "", location).strip()
    return clean_name


def process_csv(input_csv, output_csv, api_key):
    try:
        with open(input_csv, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip the header
            articles = list(reader)

        processed_articles = []
       # count = 0  # Counter to limit the number of processed entries

        for article in articles:
            # if count >= 10:
            #     break  # Stop processing after the first 10 entries
            pub_date, upd_date, location, title, _, raw_text = article
            city = clean_city_name(location)
            if city == "<NA>" or not city:
                district = 'Unknown District'
                logging.warning(f"Missing city name for article with title {title}. Using default 'Unknown District'.")
            else:
                district = get_district_by_city(city, api_key)

            vehicles, casualties, injured, reason, actions = process_raw_text(raw_text.strip('"'))
            processed_articles.append([pub_date, upd_date, location, title, vehicles, casualties, injured, reason, actions, district])
           # count += 1

        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerow(['publication_date', 'update_date', 'location', 'title', 'vehicles_involved', 'casualties', 'injured', 'reason', 'sequence_of_actions', 'district'])
            writer.writerows(processed_articles)
            logging.info("CSV processing completed successfully.")
    except Exception as e:
        logging.error(f"Error processing CSV: {e}")



print(get_district_by_city('Dhaka', api_key))
process_csv('output.csv', 'processed_accidents_data_with_district.csv', api_key)

# ROBERTA
# normalize the names because they are different
