<p align="center">
<a href="https://superagi.com//#gh-light-mode-only">
<img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
</a>
<a href="https://superagi.com//#gh-dark-mode-only">
<img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
</a>
</p>

# SuperAGI Twitter Toolkit

Introducing Twitter Toolkit for SuperAGI. With Twitter Integrated into SuperAGI, you can now deploy agents to

1. Send Tweets
2. Send Tweets with Images

## Installation

### 🛠️ Setting up SuperAGI:

Set up SuperAGI by following the instructions given [here](https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔐 Obtaining API Key and Secret from Twitter Developer Portal

1. Log in to your Twitter Developer Portal Account and select your project under the “Projects & Apps” section.

![TW1](https://github.com/Phoenix2809/SuperAGI/assets/133874957/90064a9e-321b-499e-bad1-2d6758e07252)
   
2. Proceed with creating a new app. Once you have created the app by adding a name, you will get an API Key and an API Secret, copy that and keep it in a separate text file.

![TW2](https://github.com/Phoenix2809/SuperAGI/assets/133874957/b33341af-bfe7-473f-8735-3ff19dd5370d)
![TW3](https://github.com/Phoenix2809/SuperAGI/assets/133874957/7bc79f38-32fb-4ccc-b482-cd505b6838bf)


### 🚪 Configuring OAuth

3. Once you have saved the key and the secret, click on “App Settings”
4. Once you are on the App Settings Page, start setting up the User Authentication Settings. 
    
![TW4](https://github.com/Phoenix2809/SuperAGI/assets/133874957/5b46f42b-9631-4138-92e6-3cc5e8e58863)    
    
5. Fill in the details as shown in the below image. Give “Read and Write Permissions” and make it a “Web Application"
    
![TW5](https://github.com/Phoenix2809/SuperAGI/assets/133874957/ff8bb022-ea86-4f91-b484-f7cda04226f9)
    
6. Add the Callback URI and the Website URL as shown in the image below

![TW6](https://github.com/Phoenix2809/SuperAGI/assets/133874957/e6471e3b-dc4d-4ac4-8454-4e85d086271a)
    
7. Save the settings. you have now configured OAuth Authentication for Twitter.

 ### ✅ Configuring Keys and Authenticating in SuperAGI.

1. In the SuperAGI’s Dashboard, navigate to the Twitter Toolkit Page, add the API Key and API Secret you’ve saved, and click on ‘Update Changes’

![TW7](https://github.com/Phoenix2809/SuperAGI/assets/133874957/0b5e7fd7-c1f0-4738-bacf-9aa3dbd1ef06)

2. After you’ve updated the changes, click on Authenticate. This will take you to the OAuth Flow. Authorize the app through the flow. 

![TW8](https://github.com/Phoenix2809/SuperAGI/assets/133874957/99fe96b1-350c-43b8-a269-cc68996bc080)

Once you have followe the above steps, you have successfully integrated Twitter with SuperAGI. 
