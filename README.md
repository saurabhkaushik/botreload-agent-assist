# botreload-agent-assist
Botreload Agent Assist 


<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)
[BotReload Agent Assist] (http://botreload.com/product_agentassist.html) is a Smart Reply Bot for Customer Support system which automatically identifies intent and entitites of incoming customer query and generates a reply using AI Tech (NLP / ML). This bot was launched on Zendesk in 2017, serving multiple clients with thousends of query per day. 

Key Features: 
* Suggest most Relevant Reply - Suggest quick and most relevant reply to customer query. Its algorithm is design based on Research paper published by Google.
* Cold Start Capability - Engine is trained on large enterprise helpdesk data to start serving without even any custom training.
* Continuously Serve and Learn - Its AI Engine learns from everything from past as well as present in near-realtime. It can even serve without any training (Cold start).
* Automatic ticket tagging - Agent Assist understands the content of each ticket and categorize it accordingly using both existing tags as well as newly discovered ones.
* Generates Performance Analytical Dashboard by business unit 

Key Technical Capability: 
* Automatically curates and learns Intents of queries for each business unit seprately 
* Automatically curates and generates Smart Replies for each business unit separately 

### Built With
* [Python]()
* [Scikit-learn]()
* [NLTK]()
* [Spacy]()
* [Flask]()
* [Node JS]()
* [Google Cloud Datastore]()
* [Google Cloud App Engin]()
* [Bootstrap](https://getbootstrap.com)
* [JQuery](https://jquery.com)


<!-- GETTING STARTED -->
## Getting Started

This project has two parts - Client and Server. 
* Client is Zendesk App (deployed in Zendesk Marketplace) which reads customer queries and suggests Smart Reply with confidence level. 
* Server is Smart Reply AI Engine (deployed on Google Cloud Platform - App Engine) which serves response to incoming queries from Client

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* npm
```sh
npm install npm@latest -g
```

### Installation

1. Get a free API Key at [https://example.com](https://example.com)
2. Clone the repo
```sh
git clone https://github.com/your_username_/Project-Name.git
```
3. Install NPM packages
```sh
npm install
```
4. Enter your API in `config.js`
```JS
const API_KEY = 'ENTER YOUR API';
```



<!-- USAGE EXAMPLES -->
## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_



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

Saurabh Kaushik - [@saurabhkaushik](https://twitter.com/saurabhkaushik) - support@botreload.com
Saurabh Kaushik - [@saurabhkaushik](http://www.linkedin.com/in/saurabhkaushik) - saurabh.kaushik.in@gmail.com 

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=flat-square
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=flat-square
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=flat-square
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=flat-square
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=flat-square
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=flat-square&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[npm-image]: https://img.shields.io/npm/v/datadog-metrics.svg?style=flat-square
[npm-url]: https://npmjs.org/package/datadog-metrics
[npm-downloads]: https://img.shields.io/npm/dm/datadog-metrics.svg?style=flat-square
[travis-image]: https://img.shields.io/travis/dbader/node-datadog-metrics/master.svg?style=flat-square
[travis-url]: https://travis-ci.org/dbader/node-datadog-metrics
