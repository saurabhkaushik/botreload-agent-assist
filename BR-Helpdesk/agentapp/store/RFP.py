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
import sys
sys.path.insert(0,'D:\\Users\\703201160\\PycharmProjects\\AutoResRFP\\src\\config\\')
from pathconfig import *
cfg = Configs()
st = PorterStemmer()
stops = set(stopwords.words("english"))
cust_name_list = ['GSK', 'gsk', 'Novartis','novartis']
lemma = WordNetLemmatizer()


class RfpAnswerExtractor:

    tfidf_transformer = None
    model = None
    qstn_ans_pairs = None


    # initilizing
    def __init__(self):

        model_pkl_file = cfg.nbrs_path    # 'C:/Users/gendigitalap/workspace/RFP/pickle/model.pkl'
        transformer_pkl_file = cfg.vect_path     # 'C:/Users/gendigitalap/workspace/RFP/pickle/tfidf_transformer.pkl'

        model_file = open(model_pkl_file,'rb')
        self.model = pickle.load(model_file)
        self.tfidf_transformer = pickle.load(open(transformer_pkl_file,'rb'))
        #self.qstn_ans_pairs = pd.read_excel('../data/COMBINED_RFP_DATA_excel1.xls')
        #self.qstn_ans_pairs = pd.read_csv('C:/Users/gendigitalap/workspace/RFP/data/RFP_DATA2.txt', sep='\t', encoding='utf-8')

        self.qstn_ans_pairs = pd.read_csv(cfg.input, sep='\t', encoding='utf-8')
        w2v = cfg.w2v_path  #'../w2v/doc2vec.bin'
        self.w2v_model = gensim.models.Word2Vec.load(w2v) #w2v

## find the closest synonymn from trained vocabulary
    def findClosestSyn(self, word, train_vocab):
        try:
            word_syn_lst = wn.synsets(word)
            syn_score_dict = dict()
            for syn in word_syn_lst:
                syn_word = syn.name().split('.')[0].lower()
                if syn_word!=word:
                    if syn_word in train_vocab:
                        try:
                            score = self.w2v_model.wv.similarity(syn_word,word)
                            if score>0.5:
                                syn_score_dict[syn_word] = score
                        except KeyError:
                            continue
            if len(syn_score_dict) > 0:
                sorted_syn_score = sorted(syn_score_dict.items(), key=operator.itemgetter(1), reverse=True)
                return sorted_syn_score[0][0]
        except KeyError:
            #ignore the error, the synonym. is not found
            return word


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


    def getAnswer(self,qstn):

        qstn = self.cleanData(str(qstn))
        #qstn = self.cleanData(text=qstn, lowercase = True, remove_stops = True, lemmatization = True)
        print('Clean Qstn=====================>', qstn)
        if qstn == '':
            print('No valid words', qstn)
            ans_list = 'Invalid question'
            distances = 'None'
            cust_list = "invalid"
            section_list = "invalid"
            return ans_list, distances , cust_list,  section_list
        #syn_qstn = self.replaceSynm(qstn)
        syn_qstn = qstn
        print('=====================================================')
        print('=====================================================')
        print('question : ', qstn)
        qstn_tfidf_vec = self.tfidf_transformer.transform([syn_qstn])
        print('qstn_tfidf_vec : ', qstn_tfidf_vec)
        print('type qstn_tfidf_vec : ', type(qstn_tfidf_vec))
        print(' qstn_tfidf_vec.nnz : ',  qstn_tfidf_vec.nnz)
        if( qstn_tfidf_vec.nnz != 0):  ### Case
            print('====================================>>>>>>>>>>>>')
            print('qstn_tfidf_vec : ', qstn_tfidf_vec)  #[[339 456 558 318 371 191   9 143 241  23]]
            distances, indices = self.model.kneighbors(qstn_tfidf_vec.todense())
            print('===>',indices)
            print('=====================================================')
            print('=====================================================')

            ans_list= list()
            cust_list = list()
            section_list = list()
            print(distances)
            for i in range(len(indices[0])):
                cust_list.append(self.qstn_ans_pairs.loc[indices[0][i],:].iloc[0]) ### Customer Name List
                section_list.append(self.qstn_ans_pairs.loc[indices[0][i], :].iloc[1]) ### Section Name List
                ans_list.append(self.qstn_ans_pairs.loc[indices[0][i], :].iloc[3])  ### Response
            return ans_list, distances , cust_list,  section_list
        else:  ### Case when none of the words are present in the corpus
            ans_list  = "None"
            distances = "None"
            cust_list = "None"
            section_list = "None"
            return ans_list, distances , cust_list,  section_list




if __name__ == "__main__":

    #app.run(threaded=True, port=7004)
    qstn = 'What is infrrastructure of the company'
    rfp_predict = RfpAnswerExtractor()
    rfp_predict.getAnswer()