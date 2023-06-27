<p align=center>
<a href=”https://superagi.co”><img src=https://superagi.co/wp-content/uploads/2023/05/SuperAGI_icon.png></a>
</p>

# SuperAGI Slack Toolkit

This SuperAGI Tool lets users send messages to Slack Channels and provides a strong foundation for use cases to come.

**Features:**

1. Send Message - This tool gives SuperAGI the ability to send messages to Slack Channels that you have specified.

## 🛠️ Installation

Setting up of SuperAGI:

Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Slack Configuration:**

1. Create an Application on SlackAPI Portal
    
<<<<<<< HEAD
    ![Slack_1](/README/Slack_1.png)
    
2. Select "from scratch"
    
    ![Slack_2](README/Slack_2.png)
    
3. Add your application's name and the workspace for which you'd like to use your Slack Application on
    
    ![Slack_3](README/Slack_3.png)
    
4. Once the app creation process is done, head to the "OAuth and Permissions" tab
    
    ![Slack_4](README/Slack_4.png)
=======
    ![Slack_1](/README/Slack_1.jpg)
    
2. Select "from scratch"
    
    ![Slack_2](README/Slack_2.jpg)
    
3. Add your application's name and the workspace for which you'd like to use your Slack Application on
    
    ![Slack_3](README/Slack_3.jpg)
    
4. Once the app creation process is done, head to the "OAuth and Permissions" tab
    
    ![Slack_4](README/Slack_4.jpg)
>>>>>>> 20863a5d5067f8a1b6da4c357794f036167c691a
    
5. Find the “**bot token scopes”** and define the following scopes:
    
    **"chat:write",**  and save it
    
<<<<<<< HEAD
    ![Slack_5](README/Slack_5.png)
=======
    ![Slack_5](README/Slack_5.jpg)
>>>>>>> 20863a5d5067f8a1b6da4c357794f036167c691a
    
6. Once you've defined the scope, install the application to your workspace.

    
<<<<<<< HEAD
    ![Slack_6](README/Slack_6.png)
=======
    ![Slack_6](README/Slack_6.jpg)
>>>>>>> 20863a5d5067f8a1b6da4c357794f036167c691a
    
7. Post installation, you will get the bot token code

    
<<<<<<< HEAD
    ![Slack_7](README/Slack_7.png)
    
8. Once the installation is done, you'll get the Bot User OAuth Token, which needs to be added in the config.yaml beside the **"slack_bot_token"** variable. 

![Slack_8](README/Slack_8.png)
=======
    ![Slack_7](README/Slack_7.jpg)
    
8. Once the installation is done, you'll get the Bot User OAuth Token, which needs to be added in the config.yaml beside the **"slack_bot_token"** variable. 

![Slack_8](README/Slack_8.jpg)
>>>>>>> 20863a5d5067f8a1b6da4c357794f036167c691a

Once the configuration is complete, you can install the app in the channel of your choice and create an agent on SuperAGI which can now send messages to the Slack Channel!