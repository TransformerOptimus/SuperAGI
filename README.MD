<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

<p align="center"><i>Infrastructure for building useful Autonomous Agents</i></p>

<p align="center">
<a href="https://github.com/TransformerOptimus/SuperAGI/fork" target="blank">
<img src="https://img.shields.io/github/forks/TransformerOptimus/SuperAGI?style=for-the-badge" alt="SuperAGI forks"/>
</a>
<a href="https://github.com/TransformerOptimus/SuperAGI/stargazers" target="blank">
<img src="https://img.shields.io/github/stars/TransformerOptimus/SuperAGI?style=for-the-badge" alt="SuperAGI stars"/>
</a>
<a href="https://github.com/TransformerOptimus/SuperAGI/issues" target="blank">
<img src="https://img.shields.io/github/issues/TransformerOptimus/SuperAGI?style=for-the-badge" alt="SuperAGI issues"/>
</a>
<a href="https://github.com/TransformerOptimus/SuperAGI/pulls" target="blank">
<img src="https://img.shields.io/github/issues-pr/TransformerOptimus/SuperAGI?style=for-the-badge" alt="SuperAGI pull-requests"/>
</a>
</p>

<p align="center"><b>Follow SuperAGI </b></p>

<p align="center">
<a href="https://twitter.com/_superAGI" target="blank">
<img src="https://img.shields.io/twitter/follow/_superAGI?label=Follow: _superAGI&style=social" alt="Follow _superAGI"/>
</a>

<a href="https://www.reddit.com/r/Super_AGI" target="blank">
<img src="https://img.shields.io/reddit/subreddit-subscribers/Super_AGI?label=%2Fr/Super_AGI&style=social" alt="Follow on Reddit"/>
</a>

<a href="https://discord.gg/dXbRe5BHJC" target="blank">
<img src="https://img.shields.io/discord/1107593006032355359?label=Join%20SuperAGI&logo=discord&style=social" alt="Join SuperAGI Discord Community"/>
</a>

</p>


<p align="center"><b>Share SuperAGI Repository</b></p>

<p align="center">

<a href="https://twitter.com/intent/tweet?text=Check%20this%20GitHub%20repository%20out.%20SuperAGI%20-%20Let%27s%20you%20easily%20build,%20manage%20and%20run%20useful%20autonomous%20AI%20agents.&url=https://github.com/TransformerOptimus/SuperAGI&hashtags=SuperAGI,AGI,Autonomics,future" target="blank">
<img src="https://img.shields.io/twitter/follow/_superAGI?label=Share Repo on Twitter&style=social" alt="Follow _superAGI"/></a> <a href="https://api.whatsapp.com/send?text=Check%20this%20GitHub%20repository%20out.%20SuperAGI%20-%20Let's%20you%20easily%20build,%20manage%20and%20run%20useful%20autonomous%20AI%20agents.%20https://github.com/TransformerOptimus/SuperAGI"><img src="https://img.shields.io/badge/Share-WhatsApp-green?logo=whatsapp&style=social" /></a> <a href="https://www.reddit.com/submit?url=https://github.com/TransformerOptimus/SuperAGI&title=Check%20this%20GitHub%20repository%20out.%20SuperAGI%20-%20Let's%20you%20easily%20build,%20manage%20and%20run%20useful%20autonomous%20AI%20agents.
" target="blank">
<img src="https://img.shields.io/badge/Share-Reddit-orange?logo=reddit&style=social" alt="Share on Reddit"/>
</a>

</p>

### 💡 Features

- Provision, Spawn & Deploy Autonomous AI Agents
- Extend Agent Capabilities with Tools
- Run Concurrent Agents Seamlessly
- Graphical User Interface 
- Action Console
- Multiple Vector DBs
- Multi-Modal Agents
- Agent Trajectory Fine-Tuning
- Performance Telemetry
- Optimized Token Usage
- Agent Memory Storage
- Looping Detection Heuristics 
- Concurrent Agents
- Resource Manager

### 💻 Screenshots
**CLI View**
![CLI](https://superagi.co/wp-content/uploads/2023/05/CLI.png)

**GUI (Work in progress)**

<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Light-dashboard.png" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Dark-Dashboard.png" alt="SuperAGI logo" />
  </a>
</p>


### 🛣 Roadmap
[Click here to checkout the latest roadmap 🔗](https://github.com/users/TransformerOptimus/projects/1)


### ⚙️ Setting up
**YOU NEED PINECONE SETUP FOR THIS**
1. Download the repo using `git clone https://github.com/TransformerOptimus/SuperAGI.git` in your terminal or directly from github page in zip format and unzip in your desired folder
2. Navigate to the directory using `cd SuperAGI`
3. Find the file named `config_template.yaml` and create a copy of `config_template.yaml` and name it `config.yaml`; if you want to do it in terminal window use: `cp config_template.yaml  config.yaml` (use `copy` command for windows)

4. Open the `config.yaml` file in a text editor.
5. Find the line that says `OPENAI_API_KEY`:
6. After the `:` in the respective variable assignment, enter your unique OpenAI API Key, Google key, Custom search engine ID, and Pinecone API key without any quotes or spaces. Follow the links below to get your keys:

|Keys|Accessing the keys|
|--|--|
|**OpenAI API Key**| Sign up and create an API key at [OpenAI Developer](https://beta.openai.com/signup/)|
|**Google API key**| Create a project in the [Google Cloud Console](https://console.cloud.google.com/) and enable the API you need (for example: Google Custom Search JSON API). Then, create an API key in the "Credentials" section.|
|**Custom search engine ID**| Visit [Google Programmable Search Engine](https://programmablesearchengine.google.com/about/) to create a custom search engine for your application and obtain the search engine ID.|
|**Pinecone API key**| Sign up at [Pinecone](https://www.pinecone.io/) and create an API key in your account dashboard.|

>If you're on the Pinecone free plan, you only have 1 pod and 1 index available.  As a workaround, change the index name used in test.py where `memory` is defined: `memory = VectorFactory.get_vector_storage("PineCone", "my-current-indexname", OpenAiEmbedding())`

7. Save and close the `config.yaml` file


## 🛠Setup Docker

### Windows
1. Download the appropriate Docker Desktop version for your system: [Docker for Windows](https://docs.docker.com/docker-for-windows/install/).
2. Run the `Docker Desktop Installer.exe` file, it should install Docker on your system.
> If wsl is not installed in your system, Download the [Linux Kernel Update Package](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi) and set wsl 2 as your default version by typing `wsl --set-default-version 2` into your Windows Powershell.
3. Ensure that Docker Desktop is running.
4. Check if you are SuperAGI directory in Windows Powershell. If not, use `cd` command to navigate to the SuperAGI directory
5. Run command : `docker-compose up`
6. Once your server is live, just open any browser and go to `localhost:3000`

### Mac
1. Download the appropriate Docker Desktop version for your system: [Docker for Mac](https://docs.docker.com/docker-for-mac/install/).
2. Run the `Docker.dmg` file to install docker, it should install Docker on your system.
3. Once it is installed, ensure that Docker Desktop is running.
4. Check if you are SuperAGI directory in terminal. If not, use `cd` command to navigate to the SuperAGI directory
5. Run command : `docker-compose up`
6. Once your server is live, just open any browser and go to `localhost:3000`

### Linux
1. Download the appropriate Docker Desktop version for your system: [Docker for Linux](https://docs.docker.com/desktop/install/linux-install/) 
2. Follow the steps according to your specific OS: ([Ubuntu](https://docs.docker.com/desktop/install/ubuntu/), [Debian](https://docs.docker.com/desktop/install/debian/), [Fedora](https://docs.docker.com/desktop/install/fedora/))
3. Once Docker is installed, ensure that Docker Desktop is running.
4. Check if you are SuperAGI directory in terminal. If not, use `cd` command to navigate to the SuperAGI directory
5. Run command : `docker-compose up`
6. Once your server is live, just open any browser and go to `localhost:3000`


# 🏃‍♂️ Running SuperAGI
Simply run the start script in your terminal. This will install any necessary Python packages and launch SuperAGI

* On Linux/MacOS:
`source run.sh`
* On Windows:
`.\run.bat`
> If this gives errors, make sure you have a compatible Python version installed (preferrably python 3.10).

# ⚠️ Under Development!
This project is under active development and may still have issues. We appreciate your understanding and patience. If you encounter any problems, please first check the open issues. If your issue is not listed, kindly create a new issue detailing the error or problem you experienced. Thank you for your support!


# 👩‍💻Contributors
[![TransformerOptimus](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/133493246?v=4&w=50&h=50&mask=circle)](https://github.com/TransformerOptimus) [![Cptsnowcrasher](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/133322218?v=4&w=50&h=50&mask=circle)](https://github.com/Cptsnowcrasher) [![vectorcrow](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/133646556?v=4&w=50&h=50&mask=circle)](https://github.com/vectorcrow) [![Akki-jain](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/92881074?v=4&w=50&h=50&mask=circle)](https://github.com/Akki-jain) [![Autocop-Agent](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/129729746?v=4&w=50&h=50&mask=circle)](https://github.com/Autocop-Agent)[![COLONAYUSH](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/60507126?v=4&w=50&h=50&mask=circle)](https://github.com/COLONAYUSH)[![luciferlinx101](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/129729795?v=4&w=50&h=50&mask=circle)](https://github.com/luciferlinx101)[![mukundans89](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/101278493?v=4&w=50&h=50&mask=circle)](https://github.com/mukundans89)[![Fluder-Paradyne](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/121793617?v=4&w=50&h=50&mask=circle)](https://github.com/Fluder-Paradyne)[![nborthy](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/101320057?v=4&w=50&h=50&mask=circle)](https://github.com/nborthy)[![nihirr](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/122777244?v=4&w=50&h=50&mask=circle)](https://github.com/nihirr)[![Tarraann](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/97586318?v=4&w=50&h=50&mask=circle)](https://github.com/Tarraann)[![Fluder-Paradyne](https://images.weserv.nl/?url=https://avatars.githubusercontent.com/u/121793617?v=4&w=50&h=50&mask=circle)](https://github.com/Fluder-Paradyne)


# ⭐Star History

[![Star History Chart](https://api.star-history.com/svg?repos=TransformerOptimus/SuperAGI&type=Date)](https://star-history.com/#TransformerOptimus/SuperAGI&Date)
