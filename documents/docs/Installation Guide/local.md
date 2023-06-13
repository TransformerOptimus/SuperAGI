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
  ![create-secret-key](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/f016cf35-190b-4cce-99ce-4bb7adb22b76)
  - Enter a suitable name and click on "Create secret key".
  ![create-new-key-page](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/4c739e1c-390c-4b2c-b3f6-ea8064894528)
  
#### Google API key
  - Go to [Google Cloud Console](https://console.cloud.google.com/). 
  - Click on "Select Project".
  ![select-a-project](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/b9cf1f54-8f00-4437-b017-2ca881455a36)
  - Click on "New Project".
  ![new-project](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/567be1ba-5a16-4165-b14b-096fb3cca87c)
  - Choose a suitable name and create a new project.
  ![create-new-project](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/9cecfcd9-fb32-48ba-b53d-97638b7fe7b4)
  - Go to "API and Services" from home page.
  ![home-page](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/3c90bc08-9c79-4789-8c82-96a3077f479e)
  - Click on "Credentials" and then click on "Create Credentials" on the top.
  ![create-credential](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/b45e0516-bde8-4aee-ade2-6b199550c9a7)
  - Click on "API Key" and your API Key will be created.
  ![create-api-key](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/fbffd98c-7f7e-46c3-a66f-f74004a7437b)
  
#### Custom Search Engine ID
  - Register using your gmail id.
  - Choose a suitable name and select "Search the entire web" and click on "Create".
  ![custom-search-engine](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/efa1fbd6-2449-4f60-b7c1-5a903eb90ff1)
  - Click on "Customise" and copy the "Search Engine ID".
  ![search-engine-id](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/be4fa59e-f23e-45fe-9aa8-5d7a547ab2be)

4. Ensure that Docker is installed in your system, if not, Install it from [here](https://docs.docker.com/get-docker/). 
5. Once you have Docker Desktop running, run command : `docker-compose up --build` in SuperAGI directory. Open your browser and go to `localhost:3000` to see SuperAGI running.

