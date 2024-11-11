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
   In Railway.app dashboard:
   - Go to your project
   - Click on your deployment/service
   - Go to the "Variables" tab
   - Add the following variables:
   ```
   AUTH_SECRET_KEY=<generate_a_secure_random_key>
   DEBUG=true
   AUTH_REQUIRED=true
   LOG_LEVEL=INFO
   RAILWAY_ENVIRONMENT=true
   PORT=8501
   ```

   Note: Generate a secure random key for AUTH_SECRET_KEY. Never use the default value.

4. **Deploy**
   Railway will automatically deploy your application when you push to the main branch.

5. **Verify Environment Variables**
   - Check the deployment logs to ensure variables are loaded
   - Test the application functionality
   - Verify debug logging is working if DEBUG=true

## Troubleshooting

1. **Environment Variables**
   - Check Railway.app dashboard to ensure all variables are set
   - Verify variable names match exactly (they are case-sensitive)
   - Check deployment logs for any environment-related errors

2. **Logs**
   - In Railway dashboard, check deployment logs
   - Look for environment variable loading messages
   - Enable DEBUG=true temporarily for more detailed logs

3. **Common Issues**
   - PORT conflicts: Ensure PORT is set to 8501
   - Authentication issues: Verify AUTH_SECRET_KEY is set
   - Debug mode: Set DEBUG=true to see detailed logs