# Botreload Agent Assist 
[![LinkedIn][linkedin-shield]][linkedin-url] [![Twitter][twitter-shield]][twitter-url]

<!-- ABOUT THE PROJECT -->
## About The Project
<p align="center">
<img src="http://botreload.com/img/AA-logo.jpg" alt="" title="" width="150" height="150" />
</p>

[BotReload Agent Assist](http://botreload.com/product_agentassist.html) is a Smart Reply Bot for Customer Support system which automatically identifies intent and entitites of incoming customer query and generates a reply using AI Tech (NLP / ML). This bot was launched on Zendesk in 2017, serving multiple clients with thousends of query per day. 

## Key Features: 
* Suggest most Relevant Reply - Suggest quick and most relevant reply to customer query. Its algorithm is design based on Research paper published by Google.
* Cold Start Capability - Engine is trained on large enterprise helpdesk data to start serving without even any custom training.
* Continuously Serve and Learn - Its AI Engine learns from everything from past as well as present in near-realtime. It can even serve without any training (Cold start).
* Automatic ticket tagging - Agent Assist understands the content of each ticket and categorize it accordingly using both existing tags as well as newly discovered ones.
* Generates Performance Analytical Dashboard by business unit 

## Key Technical Capability: 
* Automatically curates and learns Intents of queries for each business unit seprately 
* Automatically curates and generates Smart Replies for each business unit separately 

More internal details are at medium article. [Developing Answer Bot for Customer Service](https://medium.com/@saurabhkaushik/developing-answer-bot-for-customer-service-41e8fda71a14)

### Built With
* [Python 3.7](https://www.python.org/)
* [Scikit-learn](https://scikit-learn.org/stable/)
* [NLTK](https://www.nltk.org/)
* [Spacy](https://spacy.io/)
* [Flask](https://flask.palletsprojects.com/en/1.1.x/)
* [Node JS](https://nodejs.org/en/)
* [Google Cloud App Engine](https://cloud.google.com/appengine/)
* [Google Cloud Datastore](https://cloud.google.com/datastore)
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)

<!-- GETTING STARTED -->
## Getting Started

This project has two parts - Client and Server. 
* Client is Zendesk App (deployed in Zendesk Marketplace) which reads customer queries and suggests Smart Reply with confidence level. 
* Server is Smart Reply AI Engine (deployed on Google Cloud Platform - App Engine) which serves response to incoming queries from Client

<!-- ROADMAP -->
## Roadmap

* Intent Classification using LSTM and CNN combination  
* Response generation using Transfer Learning and GAN 

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<!-- CONTACT -->
## Contact

Saurabh Kaushik @Twitter - [@saurabhkaushik](https://twitter.com/saurabhkaushik) 

Saurabh Kaushik @LinkedIn - [@saurabhkaushik](http://www.linkedin.com/in/saurabhkaushik) 

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: http://www.linkedin.com/in/saurabhkaushik
[twitter-shield]: https://img.shields.io/twitter/follow/saurabhkaushik?style=social
[twitter-url]: https://twitter.com/saurabhkaushik 
