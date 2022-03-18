from spello.model import SpellCorrectionModel  
sp = SpellCorrectionModel(language='en')  
import pandas as pd
#from sentence_transformers import SentenceTransformer
#from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('wordnet')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import regex as re
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk.corpus import stopwords
lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()
from collections import Counter
import json
with open('Data/questionDoctorQAs.json', 'r') as datafile:
        data = json.load(datafile)
data = pd.DataFrame(data)


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

def final_clean(text):
    for i in range(len(text)):
        text[i]= re.sub("[@&!*()#$^~=;:+[<?]"," ",text[i])
        text[i]=re.sub("[.]", '', text[i])
    return text

data['cleanText']=data['answer'].map(lambda s:preprocess(s))
cnt = Counter()
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

for sent in sentences:
    for word in sent.split(' '):
        words.add(word)

words=final_clean(list(words))




sp.train(words)
sp.save(model_save_dir='Data/model.pkl')