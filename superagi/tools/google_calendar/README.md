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

![GC1](https://github.com/Phoenix2809/SuperAGI/assets/133874957/c486b2db-6cc5-46a9-8c74-59138a9ea95b)

2. After the project is created/you’re in your selected project, head to “APIs and Services”

![GC2](https://github.com/Phoenix2809/SuperAGI/assets/133874957/38a8f021-e319-406e-9622-2fb0dd94aef3)

3. Click on “ENABLED APIS AND SERVICES” and search for “Google Calendar”

![GC3](https://github.com/Phoenix2809/SuperAGI/assets/133874957/71df60bc-ce26-483c-ae3b-f3c042db26bb)

![GC4](https://github.com/Phoenix2809/SuperAGI/assets/133874957/162a27a0-35f9-41b9-ad2f-c564662c8e23)

4. Enable the API

![GC5](https://github.com/Phoenix2809/SuperAGI/assets/133874957/5bb7c785-500a-424f-ab58-5132b27c3015)

5. Once the API is Enabled, go to “OAuth Consent Screen” 

![GC6](https://github.com/Phoenix2809/SuperAGI/assets/133874957/568bc635-de35-42b9-9025-bd52ef755b43)

6. Select your User Type as “External” and click on "Create"

![GC7](https://github.com/Phoenix2809/SuperAGI/assets/133874957/8d29090b-8f9c-4e73-b0a3-b80456b6ae26)

7. Fill in the required details such as the App Information, App Domain, Authorized Domain, Developer contact information. Once filled in, click “Save and Continue” 

![GC8](https://github.com/Phoenix2809/SuperAGI/assets/133874957/bc6e3104-d462-4bb8-8c24-05d886d39310)

8. On the next page, you don’t need to select scopes. Proceed to “save and continue” and at the final page, review the process and click “Back to Dashboard”.  With this, you’ve created your OAuth Consent Screen for Google Calendar.
   
9. You can go ahead and click the “Publish App” 

![GC9](https://github.com/Phoenix2809/SuperAGI/assets/133874957/f8ca94ac-1286-4bc9-8fce-83e2f7d16903)

## 🔧 Configuring endpoints & obtaining Client ID and Client Secret Key

In order to obtain the Client ID and Secret ID, you need to do the following steps: 

1. Go to “Credentials” Page

![GC10](https://github.com/Phoenix2809/SuperAGI/assets/133874957/e9252906-5478-4a48-8a70-46b04cd20938)

2. Click on “Create Credentials” and click on “OAuth Client ID”

![GC11](https://github.com/Phoenix2809/SuperAGI/assets/133874957/a29389f7-11c5-441a-97e3-f2a5a10a98ce)

![GC12](https://github.com/Phoenix2809/SuperAGI/assets/133874957/84baecb6-c68c-4e10-8efb-430a2965db44)

3. Once you click on OAuth Client ID, choose the type of application as “Web Application” and give it a name of your choice

![GC13](https://github.com/Phoenix2809/SuperAGI/assets/133874957/5f1d83bd-f28a-4969-8e75-59582cf42a5b)

4. Create JavaScript Origins and add the following details as shown in the image: 

![Uploading GC14.png…]()

5. Go to Authorized redirect URIs and add the following as per the image: 

![GC15](https://github.com/Phoenix2809/SuperAGI/assets/133874957/9b262b0d-a8f7-4554-9ab2-a9ed7685750f)

6. Once you’re completed with adding the Authorized redirect URIs, you can click “Create” to obtain the Client ID and Client Secret Key

![GC16](https://github.com/Phoenix2809/SuperAGI/assets/133874957/be9a751d-6a62-44e5-abf7-d4cbcc8a85e6)


7. Copy the Client ID and Secret Key and save it in a file. 

## Configuring your Client ID, Secret Key and Authenticating Calendar with SuperAGI

Once the ClientID and Secret Key is obtained, you can configure and authorize Calendar to be used with SuperAGI by following these steps: 

1. Add your Client ID and Client Secret Key on the toolkit page and click on “Update Changes”

![GC_17](https://github.com/Phoenix2809/SuperAGI/assets/133874957/a56d7f03-7705-48f7-b215-8af0e79806e7)

2. Click on “Authenticate Tool” - which will now take you to the OAuth Flow. 

Once the OAuth Authentication is complete, you can now start using SuperAGI Agents with Google Calendar!
