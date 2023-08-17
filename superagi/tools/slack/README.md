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
    
![Slack_1](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/c05100b7-ca04-4da7-ad38-6ca539d5ee1d)

2. Select "from scratch"
    
![Slack_2](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/8f3ce630-8483-40e3-9026-402933eb47f7)

3. Add your application's name and the workspace for which you'd like to use your Slack Application
    
![Slack_3](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/e871e954-a4fb-4ae3-8ade-1022cdb6a613)

4. Once the app creation process is done, head to the "OAuth and Permissions" tab

![Slack_4](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/710a640c-0312-4085-a46e-1b19a13ef85f)

5. Find the “**bot token scopes”** and define the following scopes:
    
    **"chat:write",**  and save it

![Slack_5](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/48142090-00bc-4de6-9dc9-dab2e6b8ca92)

6. Once you've defined the scope, install the application to your workspace

![Slack_6](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/e348b3db-daa8-43a7-ab02-159bb12686b8)

7. Post installation, you will get the bot token code

![Slack_7](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/79e5fbc2-1554-4907-a13e-a0103793e3cb)

8. Once the installation is done, you'll get the Bot User OAuth Token, which needs to be added to the Slack Toolkit Page

![Slack_8](https://github.com/TransformerOptimus/SuperAGI/assets/133874957/d8574ffc-06d3-4099-bc07-1e16a287c192)

Once the configuration is complete, you can install the app in the channel of your choice and create an agent on SuperAGI which can now send messages to the Slack Channel.
