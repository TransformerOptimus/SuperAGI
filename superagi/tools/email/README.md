<p align="center">
<a href="https://superagi.com//#gh-light-mode-only">
<img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
</a>
<a href="https://superagi.com//#gh-dark-mode-only">
<img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
</a>
</p>

# SuperAGI Email Tool

The robust SuperAGI Email Tool lets users send and read emails while providing a foundation for other fascinating use cases.

## 💡 Features

1.**Read Emails:** With SuperAGI's Email Tool, you can effortlessly manage your inbox and ensure that you never overlook a critical detail.

2. **Send Emails:** SuperAGI's Email Tool uses its comprehensive language model capabilities to create personalised, context-aware emails, sparing you effort and time.

3. **Save Emails to Drafts Folder:** By allowing SuperAGI to develop email draughts that you can examine and modify before sending, you'll gain greater control and make sure your messages are tailored to your tastes.

4. **Send Emails with Attachments:** Send attachments in emails with ease to enrich and expand the scope of your message.

5. **Custom Email Signature:** Create a unique signature for each email you send to add a touch of customization and automation.

6. **Auto-Reply and Answer Questions:** Allow SuperAGI to read, analyse, and respond to incoming emails with precise answers to streamline your email responses.

## ⚙️ Installation

### 🛠 **Setting Up of SuperAGI**
Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Add Email configuration settings SuperAGI's Dashboard**

![Config_Page](https://github.com/Phoenix2809/SuperAGI/assets/133874957/6abe8f84-370e-4512-8374-e7eebe5f836d)

Add the following configuration in the Email Toolkit Page:

1. _Email address and password:_
 - Set 'EMAIL_ADDRESS' to sender's email address
 - Set 'EMAIL_PASSWORD' to your Password. If using Gmail, use App Password (Follow the steps given below to obtain your app password.)
 
2. _Provider-specific settings:_
 - If not using Gmail, modify 'EMAIL_SMTP_HOST', 'EMAIL_SMTP_PORT', AND 'EMAIL_IMAP_HOST' according to your email service provider.

3. _Sending and Drafts:_
	- You can set the EMAIL_DRAFT_MODE to "FALSE" if you'd like your email to be directly sent and "TRUE" if you'd like to save your emails in Draft.
	- If you're setting Draft Mode to True, Make sure to add the draft folder for your email service provider to prevent it from being sent.

4. _Optional Settings:_
 - Change the 'EMAIL_SIGNATURE' to your personalize signature.
 

## Obtain your App Password

To obtain App password for your Gmail Account follow the steps:

- Navigate to the link (https://myaccount.google.com/apppasswords)

![app_password](https://github.com/TransformerOptimus/SuperAGI/assets/97586318/ec1e6222-e5d4-4b88-a69c-1fd5774ae0ea)

- To get the App Password ensure that you have set up 2-Step Verification for your email address.

- Generate the password by creating a custom app
 
![password](https://github.com/TransformerOptimus/SuperAGI/assets/97586318/32219756-8715-4f5a-bb1c-0b2cae4e73a3)

- Copy the password generated and use it for 'EMAIL_PASSWORD'

- Also make sure IMAP Access is enabled for your Gmail Address (Settings > See all settings > Forwarding and POP/IMAP > Enable IMAP)

![imap_enable](https://github.com/TransformerOptimus/SuperAGI/assets/97586318/50ef3e0c-c2ff-4848-aba7-8a6bd4a800ab)

## Running SuperAGI Email Tool

1. **Read an email**

By default SuperAGI's email tool reads last 10 emails from your inbox, to change the limit you can modify the default limit in read_email.py 

2. **Send an email**

To send an email to a particular receiver, mention the receiver's ID in your goal. Email will be stored in drafts if in case receiver's email address is not mentioned.

![send_email](https://github.com/TransformerOptimus/SuperAGI/assets/97586318/c4dc52b9-ab68-4db3-b1f9-3431c00710c4)

3. **Send an email with attachment**

SuperAGI can send Emails with Attachments if you have uploaded the file in the Resource Manager, or if your file is in the Input or the Output of your SuperAGI Workspace. 

![attachment](https://github.com/TransformerOptimus/SuperAGI/assets/97586318/de112910-a623-469d-a0db-99063fb8572e)
```
