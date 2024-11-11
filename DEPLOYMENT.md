# Deployment Guide for Finance Dashboard

## Prerequisites

1. Create a Railway.app account
2. Install Railway CLI (optional)
3. Have Git installed

## Deployment Steps

1. **Fork and Clone the Repository**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-name>
   ```

2. **Set Up Railway Project**
   - Go to Railway.app dashboard
   - Create a new project
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Configure Environment Variables**
   In Railway.app dashboard, add the following variables:
   - `AUTH_SECRET_KEY`: Your secure secret key
   - `DEBUG`: false
   - `AUTH_REQUIRED`: true
   - `LOG_LEVEL`: INFO
   - `PORT`: 8501

4. **Deploy**
   Railway will automatically deploy your application when you push to the main branch.

5. **Verify Deployment**
   - Check the deployment logs in Railway.app dashboard
   - Visit your application URL
   - Test authentication and file upload functionality

## Troubleshooting

1. **Logs**
   - Check Railway.app deployment logs
   - Check application logs in the dashboard

2. **Common Issues**
   - Port conflicts: Make sure `PORT` environment variable is set
   - Authentication issues: Verify `AUTH_SECRET_KEY` is set
   - File permissions: Ensure temp directories are writable

## Maintenance

1. **Updates**
   - Push changes to GitHub
   - Railway will automatically redeploy

2. **Monitoring**
   - Use Railway.app metrics dashboard
   - Check application logs regularly

3. **Backup**
   - Regularly backup configuration
   - Export important data 