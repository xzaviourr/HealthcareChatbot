import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
import regex as re
import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
from collections import Counter

cnt = Counter()

def preprocess(sentence):
    sentence=str(sentence)
    sentence = sentence.lower()
    sentence=sentence.replace('{html}',"")
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', sentence)
    rem_url=re.sub(r'http\S+', '',cleantext)
    rem_num = re.sub('[0-9]+', '', rem_url)
    tokenizer = RegexpTokenizer(r'\w+')
    tokens = tokenizer.tokenize(rem_num)
    filtered_words = [w for w in tokens if len(w) > 2 if not w in stopwords.words('english')]
    stem_words=[stemmer.stem(w) for w in filtered_words]
    lemma_words=[lemmatizer.lemmatize(w) for w in stem_words]
    return " ".join(filtered_words)


def remove_freqwords(text):
    FREQWORDS = set([w for (w, wc) in cnt.most_common(60)])
    return " ".join([word for word in str(text).split() if word not in FREQWORDS])


def build_medical_dictionary():
    data = pd.read_json('Data/question-answer-dataset.json')
    data['cleanText']=data['answer'].map(lambda s:preprocess(s))
    for text in data["cleanText"].values:
        for word in text.split():
            cnt[word] += 1
    data["cleanText"] = data["cleanText"].apply(lambda text: remove_freqwords(text))
    words=set()
    for ans in data['cleanText']:
        for word in ans.split(' '):
            words.add(word)


    sentences = list()
    with open("Data/words.txt", 'r') as file:
        sentences = file.read().strip().split('\n')

    for i in range(len(sentences)):
        sentences[i]=preprocess(sentences[i])
        sentences[i]=remove_freqwords(sentences[i])

    for sentence in sentences:
        for word in sentence.split(' '):
            words.add(word)

    with open("Data/medical_words.txt", 'w') as file:
        for word in words:
            file.write(str(word))
            file.write("\n")
