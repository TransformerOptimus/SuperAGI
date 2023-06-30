<p align=center>
<a href=”https://superagi.co”><img src=https://superagi.co/wp-content/uploads/2023/05/SuperAGI_icon.png></a>
</p>

# SuperAGI Slack Toolkit

This SuperAGI Tool lets users send messages to Slack Channels and provides a strong foundation for use cases to come.

**Features:**

1. Send Message - This tool gives SuperAGI the ability to send messages to Slack Channels that you have specified.

## 🛠️ Installation

### Setting up of SuperAGI:

Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Slack Configuration:**

1. Create an Application on SlackAPI Portal
    
![Slack_1](https://github.com/Phoenix2809/SuperAGI/assets/133874957/9e612d67-439c-4e45-901a-38c61b52b08f)

2. Select "from scratch"
    
![Slack_2](https://github.com/Phoenix2809/SuperAGI/assets/133874957/c9dcfb6a-8403-49d1-bdf4-680dd1d9d8bf)

3. Add your application's name and the workspace for which you'd like to use your Slack Application on
    
![Slack_3](https://github.com/Phoenix2809/SuperAGI/assets/133874957/af21f530-25aa-4bbc-a555-3d52f9bd42eb)
    
4. Once the app creation process is done, head to the "OAuth and Permissions" tab

![Slack_4](https://github.com/Phoenix2809/SuperAGI/assets/133874957/e75e358c-2a19-4390-9928-82baa9312875)

5. Find the “**bot token scopes”** and define the following scopes:
    
    **"chat:write",**  and save it

![Slack_5](https://github.com/Phoenix2809/SuperAGI/assets/133874957/7d1d00a9-ff10-4694-9781-490e4f9b80d8)
    
6. Once you've defined the scope, install the application to your workspace.

![Slack_6](https://github.com/Phoenix2809/SuperAGI/assets/133874957/fe206e70-14d4-4595-bbcc-f92ad2a7e950)

7. Post installation, you will get the bot token code

![Slack_7](https://github.com/Phoenix2809/SuperAGI/assets/133874957/51202b97-bcf2-471c-97ca-4d83b3e6deff)
    
8. Once the installation is done, you'll get the Bot User OAuth Token, which needs to be added in the Slack Toolkit Page.

![Slack_8](https://github.com/Phoenix2809/SuperAGI/assets/133874957/2ecf1abf-1384-41f1-a317-c77d20f55330)

Once the configuration is complete, you can install the app in the channel of your choice and create an agent on SuperAGI which can now send messages to the Slack Channel!
