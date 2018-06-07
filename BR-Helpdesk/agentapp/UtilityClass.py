import pickle
import pandas as pd
import re
import gensim
import operator
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
st = PorterStemmer()
stops = set(stopwords.words("english"))
lemma = WordNetLemmatizer()

class UtilityClass: 
    
    def replaceSynm(self, txt):
        word_lst = nltk.word_tokenize(str(txt))
        chnge_word_lst = list()
        train_vocab = self.tfidf_transformer.vocabulary_
        for word in word_lst:
            word_prsnt = word in train_vocab
            if word_prsnt:
                chnge_word_lst.append(word)
            else:
                synm = self.findClosestSyn(word, train_vocab)
                if synm != None:
                    # add synonym
                    chnge_word_lst.append(synm)
                else:
                    # leave the word as it is
                    chnge_word_lst.append(word)

        return ' '.join(chnge_word_lst)


    def cleanData(self, text, lowercase=False, remove_stops=False, stemming=False, lemmatization=False):
        lowercase = True
        remove_stops = True
        stemming = True

        #txt = str(text.encode('utf-8').strip())
        txt = str(text)
        txt = re.sub(r'[^A-Za-z0-9\s]', r'', txt)
        txt = re.sub(r'\n', r' ', txt)

        txt = txt.rsplit(' ', 1)[0]  # included to remove 'get' at the end of each sentence
        #print
        if lowercase:
            txt = " ".join([w.lower() for w in txt.split()])

        if remove_stops:
            txt = " ".join([w for w in txt.split() if w not in stops])

        # Lemmatization
        if lemmatization:
            txt = " ".join([lemma.lemmatize(w) for w in txt.split()])

        if stemming:
            txt = " ".join([st.stem(w) for w in txt.split()])

        for i in range(len(cust_name_list)):
            txt = txt.replace(cust_name_list[i], 'Customer')

        return txt    
    
    def cleanhtml(raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    def preprocess(sentence):
        sentence = sentence.lower()
        tokenizer = RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(sentence)
        filtered_words = [w for w in tokens if not w in stopwords.words('english')]
        return " ".join(filtered_words)