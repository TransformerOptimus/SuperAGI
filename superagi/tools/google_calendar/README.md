<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

# SuperAGI - Google Calendar Toolkit

Introducing the Google Calendar Toolkit, a powerful integration for SuperAGI. With the Google Calendar toolkit, you have the ability to do the following:

1. **Create Calendar Events**
2. **List your Calendar Events**
3. **Fetch an event from your Calendar**
4. **Delete Calendar Events**

## ⚙️ Installation

### ⚒️ Setting up of SuperAGI

Set up SuperAGI by following the instructions given [here](https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

# ✅ Quickstart Guide:

In order to get started with integrating Google Calendar with SuperAGI, you need to do the following:

## API Creation and OAuth Consent Screen

1. Go to Google Developer Console:
[https://console.cloud.google.com/](https://console.cloud.google.com/) & Create a new project. If you’re having an existing project, you can proceed with that as well:

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/c486b2db-6cc5-46a9-8c74-59138a9ea95b" width=600px>

2. After the project is created/you’re in your selected project, head to “APIs and Services”

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/968160d6-d5bb-4e1e-9141-d993c9b5bd7c"  width=600px>



3. Click on “ENABLED APIS AND SERVICES” and search for “Google Calendar”

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/16aa1139-9f38-4938-a094-9a9ce95e721a" width=600px>
<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/bb564362-a105-4ef0-ab1c-827822550621" width=600px>

4. Enable the API
   
<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/4877001f-0ce6-4f6a-9b92-873739c0b9df" width=600px>

5. Once the API is Enabled, go to “OAuth Consent Screen” 

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/7195b562-9805-44e8-9e9d-2cea216b1447" width=600px>

6. Select your User Type as “External” and click on "Create"

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/43eb7e77-5292-4564-874b-0dea2b183c21" width=600px>

7. Fill in the required details such as the App Information, App Domain, Authorized Domain, and Developer contact information. Once filled in, click “Save and Continue” 

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/6ce9238e-d951-4fb0-bcc9-3bf054c26b95" width=600px>

8. On the next page, you don’t need to select the scopes. Proceed to “save and continue” and at the final page, review the process and click “Back to Dashboard”.  With this, you’ve created your OAuth Consent Screen for Google Calendar.
   
9. You can go ahead and click the “Publish App” 

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/9e540069-387e-407f-a4e2-bcd0ca0070aa" width=600px>

## 🔧 Configuring endpoints & obtaining Client ID and Client Secret Key

In order to obtain the Client ID and Secret ID, you need to do the following steps: 

1. Go to “Credentials” Page

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/f55aef35-df11-4f35-896a-bb9a0165a537" width=600px>

2. Click on “Create Credentials” and click on “OAuth Client ID”

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/cf2959a4-ae79-418d-ba95-09bb7cbb1b49" width=600px>

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/84baecb6-c68c-4e10-8efb-430a2965db44" width=600px>

3. Once you click on OAuth Client ID, choose the type of application as “Web Application” and give it a name of your choice

<img src="https://github.com/Phoenix2809/SuperAGI/assets/133874957/5f1d83bd-f28a-4969-8e75-59582cf42a5b" width=600px>

4. Create JavaScript Origins and add the following details as shown in the image: 

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/439b4398-bb20-4dc0-b622-bb36517ecb9b" width=600px>


5. Go to Authorized redirect URIs and add the following as per the image: 

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/f274c547-cb71-4377-807b-633fe708bea4" width=600px>

6. Once you’re completed with adding the Authorized redirect URIs, you can click “Create” to obtain the Client ID and Client Secret Key

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/17ef51d9-2e6c-4f4a-a50e-2536f6847225" width=600px>

7. Copy the Client ID and Secret Key and save it in a file. 

## Configuring your Client ID, Secret Key and Authenticating Calendar with SuperAGI

Once the ClientID and Secret Key are obtained, you can configure and authorize Calendar to be used with SuperAGI by following these steps: 

1. Add your Client ID and Client Secret Key on the toolkit page and click on “Update Changes”

<img src="https://github.com/Phoenix2809/SuperAGI/assets/92881074/c3c44790-5e89-4191-9dcd-230e7ad711b8" width=600px>

2. Click on “Authenticate Tool” - which will now take you to the OAuth Flow. 

Once the OAuth Authentication is complete, you can now start using SuperAGI Agents with Google Calendar!
