<p align=center>
<a href=”https://superagi.co”><img src=https://superagi.co/wp-content/uploads/2023/05/SuperAGI_icon.png></a>
</p>

# SuperAGI - Google Calendar Toolkit

Introducing the Google Calendar Toolkit, a powerful integration for SuperAGI. With the Gogole Calendar toolkit, you gain the ability to do the following:

1. **Create Calendar Events**
2. **List your Calendar Events**
3. **Fetch an event from your Calendar**
4. **Delete Calendar Events**

# ⚙️ Installation

### ⚒️ Setting up of SuperAGI

Set-up SuperAGI by following the instructions given [here](https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

# ✅ Quick start Guide:

In order to get started with integrating Google Calendar with SuperAGI, you need to do the following:

## API Creation and OAuth Consent Screen

1. Go to Google Developer Console:
[https://console.cloud.google.com/](https://console.cloud.google.com/) & Create a new project. If you’re having an existing project, you can proceed with that as well:

![GC1](README/GC1.png)

2. After the project is created/you’re in your selected project, head to “APIs and Services”

![GC2](README/GC2.png)

3. Click on “ENABLED APIS AND SERVICES” and search for “Google Calendar”

![GC3](README/GC3.png)

![GC4](README/GC4.png)

4. Enable the API

![GC5](README/GC5.png)

5. Once the API is Enabled, go to “OAuth Consent Screen” 

![GC6](README/GC6.png)

6. Select your User Type as “External” and click on "Create"

![GC7](README/GC7.png)

7. Fill in the required details such as the App Information, App Domain, Authorized Domain, Developer contact information. Once filled in, click “Save and Continue” 

![GC8](README/GC8.png)

8. On the next page, you don’t need to select scopes. Proceed to “save and continue” and at the final page, review the process and click “Back to Dashboard”.  With this, you’ve created your OAuth Consent Screen for Google Calendar.
   
9. You can go ahead and click the “Publish App” 

![GC9](README/GC9.png)

## 🔧 Configuring endpoints & obtaining Client ID and Client Secret Key

In order to obtain the Client ID and Secret ID, you need to do the following steps: 

1. Go to “Credentials” Page

![GC10](README/GC10.png)

2. Click on “Create Credentials” and click on “OAuth Client ID”

![GC11](README/GC11.png)

![GC12](README/GC12.png)

3. Once you click on OAuth Client ID, choose the type of application as “Web Application” and give it a name of your choice

![GC13](README/GC13.png)

4. Create JavaScript Origins and add the following details as shown in the image: 

![GC14](README/GC14.png)

5. Go to Authorized redirect URIs and add the following as per the image: 

![GC15](README/GC15.png)

6. Once you’re completed with adding the Authorized redirect URIs, you can click “Create” to obtain the Client ID and Client Secret Key

![GC16](README/GC16.png)

7. Copy the Client ID and Secret Key and save it in a file. 

## Configuring your Client ID, Secret Key and Authenticating Calendar with SuperAGI

Once the ClientID and Secret Key is obtained, you can configure and authorize Calendar to be used with SuperAGI by following these steps: 

1. Add your Client ID and Client Secret Key on the toolkit page and click on “Update Changes”

![GC17](README/GC17.png)

2. Click on “Authenticate Tool” - which will now take you to the OAuth Flow. 

Once the OAuth Authentication is complete, you can now start using SuperAGI Agents with Google Calendar!
