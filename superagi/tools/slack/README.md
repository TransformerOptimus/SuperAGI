<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

# SuperAGI Slack Toolkit

This SuperAGI Tool lets users send messages to Slack Channels and provides a strong foundation for use cases to come.

**Features:**

1. Send Message - This tool gives SuperAGI the ability to send messages to Slack Channels that you have specified

## 🛠️ Installation

### Setting up of SuperAGI:

Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Slack Configuration:**

1. Create an Application on SlackAPI Portal
    
<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/9e612d67-439c-4e45-901a-38c61b52b08f" width=600px>

2. Select "from scratch"
    
<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/c9dcfb6a-8403-49d1-bdf4-680dd1d9d8bf" width=600px>

3. Add your application's name and the workspace for which you'd like to use your Slack Application
    
<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/af21f530-25aa-4bbc-a555-3d52f9bd42eb" width=600px>
    
4. Once the app creation process is done, head to the "OAuth and Permissions" tab

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/38e8761d-5d48-4d94-bf36-0c9561a96942" width=600px>


5. Find the “**bot token scopes”** and define the following scopes:
    
    **"chat:write",**  and save it

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/7d1d00a9-ff10-4694-9781-490e4f9b80d8" width=600px>
    
6. Once you've defined the scope, install the application to your workspace

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/fe206e70-14d4-4595-bbcc-f92ad2a7e950" width=600px>

7. Post installation, you will get the bot token code

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/10581710-12e5-4bc8-a1e8-18d1a892faff" width=600px>


8. Once the installation is done, you'll get the Bot User OAuth Token, which needs to be added in the Slack Toolkit Page

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/2ecf1abf-1384-41f1-a317-c77d20f55330" width=600px>

Once the configuration is complete, you can install the app in the channel of your choice and create an agent on SuperAGI which can now send messages to the Slack Channel.
