# GitHub Codespaces
<iframe width="800" height="450" src="https://www.youtube-nocookie.com/embed/iSPHZ1onQ44?controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



1. Open the SuperAGI GitHub repository `https://github.com/TransformerOptimus/SuperAGI/` and click on `Code > Codespaces > Create new codespace`
2. Navigate to the directory and create a copy of `config_template.yaml` and name it `config.yaml`.
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
  
5. Open up the terminal at the bottom of the codespace and run the following command: `docker compose up --build` and wait for the build to complete.
6. Go to the 'Ports' tab, copy the 8001 and 3000 public addresses. Replace the `localhost` link in the `docker-compose.yaml` file with the 8001 public address, and paste the 3000 public address as a string into the `main.py` file.
7. Make sure to remove the trailing forward slash from the end of URL in both places.
8. Run the `docker compose up --build` command again.
9. Once the build is complete, change the visibility of both ports to public and open the 3000 public URL in a new tab.

You are now ready to expplore SuperAGI.


