#import matplotlib.pyplot as plt 
from gensim.models.word2vec import Word2Vec
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline
import re 
import numpy as np
from pandas_ml import ConfusionMatrix 
from sklearn.metrics import  f1_score, precision_score, recall_score
import nltk
import csv
from nltk import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tag import StanfordNERTagger
from gensim.models import word2vec
from collections import defaultdict

dict_file = 'input/dictionary.txt'
TRAIN_SET_PATH = 'input/samplemail.txt'
TEST_SET_PATH = 'input/testmail.txt'
GLOVE_6B_50D_PATH = "input/glove.6B.50d.txt"
txt_modelfile = 'input/text8.model.bin'
ner_datafile = '../libs/stanford-ner-2016-10-31/classifiers/english.all.3class.distsim.crf.ser.gz'
ner_jarfile = '../libs/stanford-ner-2016-10-31/stanford-ner.jar'

class MeanEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.dim = len(word2vec.items())
    
    def fit(self, X, y):
        return self 

    def transform(self, X):
        return np.array([
            np.mean([self.word2vec[w] for w in words if w in self.word2vec] 
                    or [np.zeros(self.dim)], axis=0)
            for words in X
        ])
    
# and a tf-idf version of the same
class TfidfEmbeddingVectorizer(object):
    def __init__(self, word2vec):
        self.word2vec = word2vec
        self.word2weight = None
        self.dim = len(word2vec.items())
        
    def fit(self, X, y):
        tfidf = TfidfVectorizer(analyzer=lambda x: x)
        tfidf.fit(X)
        # if a word was never seen - it must be at least as infrequent
        # as any of the known words - so the default idf is the max of 
        # known idf's
        max_idf = max(tfidf.idf_)
        self.word2weight = defaultdict(
            lambda: max_idf, 
            [(w, tfidf.idf_[i]) for w, i in tfidf.vocabulary_.items()])
    
        return self
    
    def transform(self, X):
        return np.array([
                np.mean([self.word2vec[w] * self.word2weight[w]
                         for w in words if w in self.word2vec] or
                        [np.zeros(self.dim)], axis=0)
                for words in X
            ])

class EntityExtractor(object):
    
    def __init__(self):
        self.nounkey = ['NN', 'NNP', 'NNPS', 'NNS', 'JJ', 'VBD', 'VBN', 'VB', 'VBZ']
        self.C = ['CD', 'NNP','JJ' ]  
        self.intentDict = {}
        #self.d = defaultdict(list)
        self.__storage1 = []
        self.__storage2 = []
        self.l=[]
        self.m=[]
        
        with open(dict_file, mode='r') as infile:
            reader = csv.reader(infile)
            self.intentDict = {rows[0]:rows[1:] for rows in reader}
        """
        with open(dict_file, 'r') as f:
            data = [line.strip().split() for line in f.readlines()]
            self.intentDict = {d[0]: d[1:] for d in data}
          
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
        
        self.sentences = word2vec.Text8Corpus('../input/text8')
        
        self.model = word2vec.Word2Vec(sentences, size=200)
        
        # store the learned weights, in a format the original C tool understands
        self.model.save_word2vec_format(txt_modelfile, binary=True)
        
        """ 
        # import word weights created by the (faster) C word2vec
        #self.model = word2vec.Word2Vec.load_word2vec_format(txt_modelfile, binary=True) 
            
    def POS_Tagging(self,Email_Content):
        self.model = word2vec.Word2Vec.load_word2vec_format(txt_modelfile, binary=True) 
        #st = StanfordNERTagger(ner_datafile, ner_jarfile, encoding='utf-8')
        self.d = defaultdict(list)
        print("\n" + "################# intent and Entity ################################" + "\n")
        sentences = nltk.sent_tokenize(Email_Content)
        for stxf in sentences:
            tokens = word_tokenize(stxf)
            tokens_pos = pos_tag(tokens)
            classified_text = '' #st.tag(tokens)
            # classified_text = st.tag(tokens)
            print("\nEmail Contents : ", stxf)
            print('Sentence POS : ', tokens_pos)
            chunkGram = r"""NP:{<NN.*>*<JJ|VB.*>?<IN>?<\#|\$>?<NNP>?<JJ>?<:|,|CD>*}"""
            chunkParser = nltk.RegexpParser(chunkGram)
            chunked = chunkParser.parse(tokens_pos)
            for subtree in chunked.subtrees(filter=lambda t: t.label() == 'NP'):
                # print(subtree)
                verbcontents = subtree.leaves()
                print (verbcontents)
                for sn_pos_t in verbcontents:  # It will go with the each element of chunk [('payment', 'NN'), ('of', 'IN'), ('$', '$'), ('2000', 'CD')]
                    if sn_pos_t[1] in self.nounkey:
                        nword = sn_pos_t[0].lower()
                        for key, values in self.intentDict.items():  # It will go with the size of dictionary
                            for item in values:
                                try:
                                    result = self.model.similarity(nword, item)
                                    #print("model.similarity(" + nword + "," + item + ")", result)
                                    if result >= (.99):
                                        for c_pos_t in verbcontents:
                                            if c_pos_t[1] in self.C:
                                                val = c_pos_t[0].isalpha()
                                                if(val == False):
                                                    print("after similarity test")
                                                    print("model.similarity(" + nword + "," + item + ")", result)
                                                    mat=re.match('(\d{2})[/.-](\d{2})[/.-](\d{4})$', c_pos_t[0])
                                                    if mat is not None:
                                                        self.d["Date"].append(c_pos_t[0])
                                                        print("Date = " +c_pos_t[0])
                                                    elif key == "Amount":
                                                        k=c_pos_t[0].replace(",", "")
                                                        self.d[key].append(k)
                                                        print(key+" = "+k)
                                                    else:
                                                        self.d[key].append(c_pos_t[0])
                                                        print(key+" = "+c_pos_t[0])
                                                    #print("----------------Mapped intent value : " + key)
                                                    #print(key + " = " + c_pos_t[0])
                                                    #self.d[key].append(c_pos_t[0])
                                except KeyError:
                                    break 
            
            for item in classified_text:
                print (item)
                if item[1] == 'ORGANIZATION':
                    self.push1(item[0])
                elif item[1] == 'PERSON':
                    self.push2(item[0])
                elif item[1] == 'O':
                    self.isEmpty() 
        return self.d
                
    def isEmpty(self):
        if len(self.__storage1) != 0:
            self.pop1()
        elif len(self.__storage2) != 0:
            self.pop2()    

    def push1(self,p):
        self.__storage1.append(p)
    
    def push2(self,p):
        self.__storage2.append(p)    

    def pop1(self):
        m=[]
        l=""
        a=len(self.__storage1)
        while a>0:
            m=self.__storage1.pop(0)
            l=l+" "+m
            a=a-1 
        self.d["AccountName"].append(l)       
    def pop2(self):
        m=[]
        l=""
        a=len(self.__storage2)
        while a>0:
            m=self.__storage2.pop(0)
            l=l+" "+m
            a=a-1
        self.d["CustomerName"].append(l)