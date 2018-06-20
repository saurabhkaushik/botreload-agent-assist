from textacy.preprocess import preprocess_text
from agentapp.UtilityClass import UtilityClass

junk_list = ['NAME', 'EMAIL', 'NUMBER', 'URL']

class UtilityClass_spacy:  
    
    def preprocessText(self, strtxt, lowercase=True, no_punct=True): 
        self.utilclass = UtilityClass()
        strtxt = str(strtxt)
        posttxt = preprocess_text(strtxt,
                           fix_unicode=True,
                           lowercase=lowercase,
                           transliterate=True,
                           no_urls=True,
                           no_emails=True,
                           no_phone_numbers=True,
                           no_numbers=True,
                           no_currency_symbols=True,
                           no_punct=no_punct,
                           no_contractions=False,
                           no_accents=True)
        for i in range(len(junk_list)):
            posttxt = posttxt.replace(junk_list[i], '')
        return posttxt