---
sidebar_position: 1
---

# Win/MacOS/Linux
<iframe width="800" height="450" src="https://www.youtube.com/embed/3xnx-T7jL_w" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



1. Download the repo using `git clone https://github.com/TransformerOptimus/SuperAGI.git` in your terminal or directly from github page in zip format.
2. Navigate to the directory using `cd SuperAGI` and create a copy of `config_template.yaml` and name it `config.yaml`.
3. Enter your unique OpenAI API Key, Google key, Custom search engine ID without any quotes or spaces in `config.yaml` file. Follow the links below to get your keys:

#### OpenAI API Key
  - Go to https://beta.openai.com/signup/ and click on your name on the Top-Right of the Screen. Click on "View API Keys".
  - Click on "Create new secret key". 
  - Enter a suitable name and click on "Create secret key".
#### Google API key
  - Go to [Google Cloud Console](https://console.cloud.google.com/). 
  - Click on "Select Project".
  - Click on "New Project".
  - Choose a suitable name and create a new project.
  - Go to "API and Services" from home page.
  - Click on "Credentials" and then click on "Create Credentials" on the top. 
  - Click on "API Key" and your API Key will be created.
#### Custom Search Engine ID
  - Register using your gmail id.
  - Choose a suitable name and select "Search the entire web" and click on "Create".
  - Click on "Customise" and copy the "Search Engine ID".

4. Ensure that Docker is installed in your system, if not, Install it from [here](https://docs.docker.com/get-docker/). 
5. Once you have Docker Desktop running, run command : `docker-compose up --build` in SuperAGI directory. Open your browser and go to `localhost:3000` to see SuperAGI running.

