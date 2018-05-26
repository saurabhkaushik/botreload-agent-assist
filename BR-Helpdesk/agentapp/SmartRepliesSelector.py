from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score

class SmartReplySelector(object):

    def __init__(self):
        self.client = datastore.Client()
        self.storage_client = storage.Client()
    # [END build_service]  
    
    def prepareTrainingData(self, cust_id):
        logging.info("\n"+"################# Preparing Training Data ################################"+"\n")
        self.X, self.y = [], []
        
        tickets_learn = tickets_learner()
        ticket_data = tickets_learn.getTrainingData(cust_id=cust_id)
    
        xX = []
        yY = []
        for linestms in ticket_data:           
            for linestm in linestms:
                logging.debug (linestm['tags'] + " =>  " + linestm['resp_category'])
                xX_query.append(preprocess(str(linestm['query'])).strip())
                xX_response.append(preprocess(str(linestm['response'])).strip())
                yY.append(linestm['resp_category'].strip())
        self.X_q = xX_query
        self.X_r = xX_response
        self.y = yY
        
        self.X, self.y = np.array(self.X, dtype=object), np.array(self.y, dtype=object)
        logging.info ("Total Training Examples : %s" % len(self.y))
    
    def getKMeanClusters(self):
        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(self.X_q)
        
        true_k = 2
        model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
        model.fit(X)
        
        print("Top terms per cluster:")
        order_centroids = model.cluster_centers_.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names()
        for i in range(true_k):
            print("Cluster %d:" % i),
            for ind in order_centroids[i, :10]:
                print(' %s' % terms[ind]),
            print
        
        print("\n")
        print("Prediction")
        
        Y = vectorizer.transform(["chrome browser to open."])
        prediction = model.predict(Y)
        print(prediction)
        
        
#   def getNearestNeighbore(self):
    
#   def getMostFrequentInCluster(self): 
        




