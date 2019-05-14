# Instant View Issue Finder
In 2017 and 2019 the team behind the messenger [Telegram](https://telegram.org) organized two Instantview contests. Participants created so-called "templates" which use XPath to parse articles on websites into the Instantview format. Other contestants and users could create issues (similar to GitHub issues) when they found problems with a certain template. 
This tool helped to obtain a summary of all the unhandled and closed issues during the contest. 

### What is Instantview?
[Telegram Instantview](https://instantview.telegram.org/) is a feature of the messenger Telegram, which offers an in-app, stripped versions of websites, especially news articles. It's compareable with [Google AMP](https://en.wikipedia.org/wiki/Accelerated_Mobile_Pages) or [Facebook Instant Articles](https://en.wikipedia.org/wiki/Facebook_Instant_Articles).
Also you might know a similar feature from firefox, it's called ["Reader View"](https://support.mozilla.org/en-US/kb/firefox-reader-view-clutter-free-web-pages).
One of the best parts of it is that Telegram caches the articles (also media) on their servers, which makes them load in a fraction of a second, even with quite low connections. 

### What does this tool do?
This tool parses the Telegram contest website for active domains and checks the templates on these domains for issues. It eventually generates output files which can be used further to e.g. display the data on a webpage or to do some statistics. The data is available as `.csv` and `.json`.

### Components
This software is made up of two components - the `backend` component, which contains all the code to parse the issues from the official Telegram website and the frontend or rather `website` component.
To use the parser, you need to use the `./backend/main.py` file, and add your own code, depending on what data you want to retrieve.

Since this was not planned to be made public in the first place, there is no proper documentation. Feel free to ask me about it, if you have questions.
