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

class app_namespace_manager(object):
    self.namespace = 
    def getNamespace (self): 
        
    def setNamespace(self, namespace='default'):
        # Save the current namespace.
        previous_namespace = namespace_manager.get_namespace()
        try:
            namespace_manager.set_namespace(namespace)
            print ('Setting namespace : ' + namespace)
        finally:
            # Restore the saved namespace.
            namespace_manager.set_namespace(previous_namespace)