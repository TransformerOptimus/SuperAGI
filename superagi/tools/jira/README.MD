<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

# SuperAGI Jira Tool

The SuperAGI Jira Tool lets users create, edit and search issues while providing a foundation for other great use cases.

## 💡 Features

1.**Create Issue:** SuperAGI's JIRA tool lets you seamlessly create new tasks in your project by defining the task's details such as its summary, description, type, and priority. 

2. **Edit Issue:** Modify existing tasks quickly with SuperAGI's JIRA tool, which allows you to change any task details like summary, description, type, and priority.

3. **Search Issues:** Use the powerful 'Search Issues' feature to find specific tasks within your projects by defining your search criteria in terms of project, assignee, or keywords in the task summary.

4. **Get Projects:** Discover and access all your projects with ease using the 'Get Projects' feature, providing a bird's eye view of your workload and streamlining project-based searches.

## ⚙️ Installation

### 🛠 **Setting Up of SuperAGI**
Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Add Jira configuration settings in SuperAGI Dashboard**
Add the following configuration settings in the file:

1. _JIRA API TOKEN:_
 - Login into your Jira Account. Go to "Manage Account".
 - Go to Security and click on "Create and Manage API Tokens".

<img src="https://github.com/TransformerOptimus/SuperAGI/assets/43145646/b9a535be-0f44-40f8-aec5-4f09bd223c9e" width=600px>

 - Click on "Create API Token" and choose an appropriate label name.
 - Copy the API Token and save it in a text file.

2. _JIRA INSTANCE URL:_
 - Your instance profile is the section at the start of your URL. It should look something like "https://mycompany.atlassian.net/".

3. _JIRA USERNAME:_
 - Your Jira UserName is the Email Address with which you signed up in Jira.

4. _CONFIGURING JIRA IN SUPERAGI DASHBOARD:_ 
 - Open the Jira Toolkit Page in SuperAGI Add your Jira API Token, your Instance URL, and your Jira Username and click "Update Changes"

## Running SuperAGI Jira Tool

1. **Create an Issue:** The SuperAGI JIRA Create Issue tool allows you to create issues in your project. By default, it creates a task with predefined settings. To create a task with different details, modify the relevant fields in the create_issue.py script.

2. **Edit an Issue:** To edit a particular issue, specify the issue ID in your goal. The modifications can be made by changing the relevant fields in the edit_issue.py script.

3. **Search for Issues:** You can simply search for a particular issue in your agent's goals and your agent performs a search based on the JIRA Query Language (JQL) query you define. Modify the JQL query according to your requirements in the search_issues.py script.

4. **Fetch Project Details:** Use the 'Get Projects' feature to retrieve a list of your accessible projects. The get_projects.py script can be modified to adjust the parameters of this operation.
