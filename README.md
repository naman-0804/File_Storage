# Google Drive API Integration for File Uploads

## Overview

This report provides an overview of the steps involved in integrating the **Google Drive API** with a service account to automate file uploads from a web application to Google Drive. This solution eliminates the need for user login, allowing files to be uploaded directly to Google Drive with security and automation.

---

## Process Breakdown

### 1. Setting Up Google Cloud Project

- **Create a Google Cloud project**: Start by creating a new project in the [Google Cloud Console](https://console.cloud.google.com).
- **Enable Google Drive API**: Enable the **Google Drive API** to allow your backend to interact with Google Drive.

### 2. Creating a Service Account

- **Create a service account**: Navigate to **IAM & Admin > Service Accounts** in the Google Cloud Console and create a new service account with appropriate permissions.
- **Generate a JSON key**: After creating the service account, generate a **JSON key**. This key will be used to authenticate the backend code, allowing it to access Google Drive programmatically.

### 3. Sharing a Google Drive Folder

- **Create a folder** in Google Drive (e.g., `AutoUploads`).
- **Share the folder with the service account**: In order for the service account to upload files, it needs permission to access the folder. Share the folder with the service account’s email address, granting it **Editor** permissions.

# Step-by-Step Guide to Use This on Render

## 1. Set Up Google API Credentials on Render

1. **Go to Render Dashboard**: Open [Render Dashboard](https://dashboard.render.com/) and log into your account.
2. **Navigate to Your Service**: Go to the service where you want to deploy the application (e.g., Flask app).
3. **Open the Environment Tab**: Inside your service, click on the **Environment** tab.
4. **Add Google Drive API Credentials**: 
   - Create a new environment variable (e.g., `GOOGLE_APPLICATION_CREDENTIALS_JSON`).
   - Paste the entire **contents of the JSON credentials file** as the value of the environment variable. 
   - Save the environment variable.


## 2. Deploy Your Application on Render

- **Push the code to GitHub** (if not already there) and connect it to **Render**.
- **Deploy your app**: After connecting your GitHub repository to Render, deploy your Flask app.
- **Verify the deployment**: Once the app is deployed, test uploading a file to confirm that everything is working and files are being uploaded to Google Drive.

## 3. Security Considerations

- **Never push your Google API credentials file to GitHub**. Always use **environment variables** for security.
- Render stores environment variables securely, ensuring your credentials are safe.
