---
sidebar_position: 1
---

# Win/MacOS/Linux
<iframe width="800" height="450" src="https://www.youtube.com/embed/3xnx-T7jL_w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



1. Download the repo using `git clone https://github.com/TransformerOptimus/SuperAGI.git` in your terminal or directly from github page in zip format.
2. Navigate to the directory using `cd SuperAGI` and create a copy of `config_template.yaml` and name it `config.yaml`.
3. Enter your unique OpenAI API Key, Google key, Custom search engine ID without any quotes or spaces in `config.yaml` file. Follow the links below to get your keys:

|Keys|Accessing the keys|
|--|--|
|**OpenAI API Key**| Sign up and create an API key at [OpenAI Developer](https://beta.openai.com/signup/)|
|**Google API key**| Create a project in the [Google Cloud Console](https://console.cloud.google.com/) and enable the API you need (for example: Google Custom Search JSON API). Then, create an API key in the "Credentials" section.|
|**Custom search engine ID**| Visit [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/) to create a custom search engine for your application and obtain the search engine ID.|

4. Ensure that Docker is installed in your system, if not, Install it from [here](https://docs.docker.com/get-docker/). 
5. Once you have Docker Desktop running, run command : `docker-compose up --build` in SuperAGI directory. Open your browser and go to `localhost:3000` to see SuperAGI running.

