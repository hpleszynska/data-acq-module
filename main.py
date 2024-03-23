import csv
import re
import nltk
import string
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

def sum_numbers(*args):
    return sum(int(num) if num.isdigit() else 0 for num in args)

def find_casualties(raw_text):
#   tokenizing and POS tagging
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
                                injured.append(leaf[0])
                                number = 1
                                break
                        if len(injured) == 0:
                            injured.append('one')
                    # if tree.leaves().count('died') > 0 or tree.leaves().count('killed') > 0:
                    #     killed.append(tree.leaves())
                    # elif tree.leaves().count('injured') > 0:
                    #     injured.append(tree.leaves())

    return killed, injured

def process_raw_text(raw_text):
    lines = raw_text.split('\n')
    vehicles_involved = set()
    total_casualties, total_injured = 0, 0
    reason, sequence_of_actions = '', ''

    vehicles_pattern = re.compile(r'(trucks?|motorcycles?|autorickshaws?|buses?|cars?|SUVs?|microbuses?|trains?|microbus?)', re.IGNORECASE)
    reason_patterns = [r'lost control', r'speeding', r'crashed into', r'collision']
    sequence_patterns = [r'on the way', r'leading up to the accident', r'before the accident']

    total_casualties, total_injured = find_casualties(raw_text)

    for line in lines:
        for match in vehicles_pattern.finditer(line):
            vehicles_involved.add(match.group(0).lower())

        for pattern in reason_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                reason += line + '. '

        for pattern in sequence_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                sequence_of_actions += line + '. '

    vehicles_str = ', '.join(sorted(vehicles_involved))
    return vehicles_str, str(total_casualties), str(total_injured), reason, sequence_of_actions

def process_csv(input_csv, output_csv):
    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        articles = list(reader)

    processed_articles = []

    for article in articles:
        publication_date, update_date, location, title, _, raw_text = article
        vehicles_involved, casualties, injured, reason, sequence_of_actions = process_raw_text(raw_text.strip('"'))
        processed_article = [publication_date.strip('<>'), update_date.strip('<>'), location.strip('<>'), title.strip('<>'), vehicles_involved, casualties, injured, reason, sequence_of_actions]
        processed_articles.append(processed_article)

    with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['publication_date', 'update_date', 'location', 'title', 'vehicles_involved', 'casualties', 'injured', 'reason', 'sequence_of_actions'])
        writer.writerows(processed_articles)

# Replace 'output.csv' and 'processed_accidents_data.csv' with your actual file paths
process_csv('output.csv', 'processed_accidents_data2.csv')
