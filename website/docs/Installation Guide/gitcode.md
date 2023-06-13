# GitHub Codespaces
<iframe width="800" height="450" src="https://www.youtube-nocookie.com/embed/iSPHZ1onQ44?controls=0" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>



1. Open the SuperAGI GitHub repository `https://github.com/TransformerOptimus/SuperAGI/` and click on `Code > Codespaces > Create new codespace`
2. Navigate to the directory and create a copy of `config_template.yaml` and name it `config.yaml`.
3. Enter your unique OpenAI API Key, Google key, Custom search engine ID without any quotes or spaces in `config.yaml` file. Follow the links below to get your keys:

|Keys|Accessing the keys|
|--|--|
|**OpenAI API Key**| Sign up and create an API key at [OpenAI Developer](https://beta.openai.com/signup/)|
|**Google API key**| Create a project in the [Google Cloud Console](https://console.cloud.google.com/) and enable the API you need (for example: Google Custom Search JSON API). Then, create an API key in the "Credentials" section.|
|**Custom search engine ID**| Visit [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/) to create a custom search engine for your application and obtain the search engine ID.|
 
5. Open up the terminal at the bottom of the codespace and run the following command: `docker compose up --build` and wait for the build to complete.
6. Go to the 'Ports' tab, copy the 8001 and 3000 public addresses. Replace the `localhost` link in the `docker-compose.yaml` file with the 8001 public address, and paste the 3000 public address as a string into the `main.py` file.
7. Make sure to remove the trailing forward slash from the end of URL in both places.
8. Run the `docker compose up --build` command again.
9. Once the build is complete, change the visibility of both ports to public and open the 3000 public URL in a new tab.

You are now ready to expplore SuperAGI.


