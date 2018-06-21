from textacy.preprocess import preprocess_text
from agentapp.UtilityClass import UtilityClass
#import spacy

langsup = {'da' : 'danish', 'nl' : 'dutch', 'en': 'english', 'fi': 'finnish', 'fr' : 'french', 'de' : 'german', 
           'hu' : 'hungarian', 'it': 'italian', 'no': 'norwegian', 'pt':  'portuguese', 'ru': 'russian', 'es': 'spanish', 
           'sv': 'swedish', 'tr': 'turkish'}

class UtilityClass_spacy:  
    
    def preprocessText(self, strtxt, lang = 'en', ner=False): 
        self.utilclass = UtilityClass()
        posttxt = str(strtxt)
        '''
        if ner: 
            posttxt = self.processNER(posttxt, lang=lang)
        '''
        posttxt = preprocess_text(posttxt,
                           fix_unicode=True,
                           lowercase=False,
                           transliterate=False,
                           no_urls=True,
                           no_emails=True,
                           no_phone_numbers=True,
                           no_numbers=True,
                           no_currency_symbols=True,
                           no_punct=False,
                           no_contractions=False,
                           no_accents=False)   
        return posttxt
    '''
    def processNER(self, textstr, lang = 'en'):
        nlp = spacy.load('en_core_web_sm')
        doc = nlp(textstr)
        textout = textstr
        for ent in doc.ents:
            textout = textstr.replace(ent.text, str(ent.label_))
        return textout 
    '''