<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

# SuperAGI GitHub Tool

The SuperAGI GitHub Tool enables users to perform various operations on GitHub repositories which include adding files or folders, deleting files, and searching for files or folders within a repository.

## 💡 Features

1. **Add Files or Folders:** With SuperAGI's GitHub Tool, you can easily add files or folders to a GitHub repository
2. **Delete Files:** Remove files from a GitHub repository effortlessly using SuperAGI's GitHub Tool. 
3. **Search for Files or Folders:** Find specific files or folders within a GitHub repository using SuperAGI's GitHub Tool. 

## ⚙️ Installation

### 🛠 **Setting Up SuperAGI**

Set up SuperAGI by following the instructions provided in the [SuperAGI repository's README file](https://github.com/TransformerOptimus/SuperAGI/blob/main/README.md).

### 🔧 **Add GitHub Configuration Settings in SuperAGI Dashboard**

Add the following configuration settings to the GitHub Toolkit Page:

1. _GitHub Access Token:_
   - Obtain a GitHub access token with the necessary permissions for accessing and modifying repositories.
    - Go to Settings in your GitHub Account. Then go to Developer Settings.
    - Click on "Personal access tokens". Then click on "Tokens (classic)".
    ![personal-access-token](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/ee646cdd-fa04-400b-ae84-e9aee7b46c36)
    - Click on "Generate new token". Then choose "Generate new token (classic)".
    ![generate-new-token](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/64f1d681-236a-4008-a5d9-93bb368caaaf)
    - Write a Note about what the token is for and choose an appropriate expiration date.
    ![github-permissions](https://github.com/TransformerOptimus/SuperAGI/assets/43145646/757b02e8-0b49-47b8-bfef-5469c0d070eb)
    - Select all the scopes (In this way, users won't have to create new Access Tokens every time we add new scopes to the code).
    - Click on Generate New Token.
    - Copy the token and save it as a separate file. 

2. _Github User Name:_
   - You can find your GitHub username on your GitHub Profile.

3. _Configuring in SuperAGI Dashboard:_
   -You can add your Generated Token and your Username to the GitHub Toolkit Page.

## Running SuperAGI GitHub Tool

1. **Add Files or Folders:**

   To add a file or folder to a GitHub repository, specify the repository and the owner's UserName and the path where the file/folder should be added to your goal. SuperAGI will upload it to the repository and automatically raise a PR for it. By default, it'll pick the main branch, if you want to add it to any other branch you have to mention it in the goal.

2. **Delete Files:**

   To delete a file from a GitHub repository, mention the repository, owner's UserName and provide the path to the file you want to delete in your goal. SuperAGI will handle the deletion process and raise a PR for it. By default, it'll pick the main branch, if you want to delete it to any other branch you have to mention it in the goal.

3. **Search for Files or Folders**

   To search for files or folders within a GitHub repository, specify the repository, and owner's UserName and provide the name or path of the file/folder you're looking for in your goal. SuperAGI will provide you with the search results. By default, it'll pick the main branch, if you want to search in any other branch you have to mention it in the goal.
 
