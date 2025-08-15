# 🚀 Azure Setup Guide for BASF Feedback Analysis App

This guide walks you through setting up Azure resources for deploying your React + Flask feedback analysis application. Complete these steps before running the deployment scripts.

## Prerequisites

- Azure account with active subscription
- Azure CLI installed ([Download here](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli))
- GitHub account with your code repository

## 📋 Setup Checklist

### Step 1: Azure CLI Login

```bash
# Login to Azure
az login

# Verify your subscription
az account show

# Set subscription if you have multiple
az account set --subscription "Your-Subscription-Name"
```

### Step 2: Register Required Resource Providers
```bash
# Register required Azure resource providers (required for new subscriptions)
az provider register --namespace Microsoft.Web
az provider register --namespace Microsoft.Insights
az provider register --namespace Microsoft.Storage

# Wait for registration to complete (takes 1-2 minutes)
az provider show --namespace Microsoft.Web --query "registrationState"
```

### Step 3: Create Resource Group

```bash
# Create a resource group (choose your preferred region)
az group create --name "basf-feedback-rg" --location "East US"
```

### Step 4: Create Azure App Service Plan

```bash
# Create App Service Plan (Free tier for demo)
az appservice plan create \
  --name "basf-feedback-plan" \
  --resource-group "basf-feedback-rg" \
  --sku FREE \
  --is-linux
```

### Step 5: Create Web App for Backend

```bash
# Create Flask backend web app
az webapp create \
  --name "basf-feedback-api" \
  --resource-group "basf-feedback-rg" \
  --plan "basf-feedback-plan" \
  --runtime "PYTHON:3.11" \
  --deployment-source-url "https://github.com/YOUR-USERNAME/YOUR-REPO-NAME"
```

### Step 6: Configure Environment Variables for Backend

```bash
# Set environment variables for your Flask app
az webapp config appsettings set \
  --name "basf-feedback-api" \
  --resource-group "basf-feedback-rg" \
  --settings \
    AZURE_TEXT_ANALYTICS_KEY="your-text-analytics-key" \
    AZURE_TEXT_ANALYTICS_ENDPOINT="your-text-analytics-endpoint" \
    AZURE_SPEECH_KEY="your-speech-key" \
    AZURE_SPEECH_REGION="your-speech-region" \
    OPENAI_API_KEY="your-openai-key" \
    OPENAI_MODEL="gpt-4o" \
    SECRET_KEY="your-secure-secret-key" \
    FLASK_ENV="production"
```

### Step 7: Create Static Web App for Frontend

```bash
# Create Static Web App for React frontend
az staticwebapp create \
  --name "basf-feedback-frontend" \
  --resource-group "basf-feedback-rg" \
  --source "https://github.com/YOUR-USERNAME/YOUR-REPO-NAME" \
  --location "East US 2" \
  --branch "main" \
  --app-location "/frontend" \
  --output-location "dist"
```

### Step 8: Configure CORS for Backend

```bash
# Enable CORS for your frontend domain
az webapp cors add \
  --name "basf-feedback-api" \
  --resource-group "basf-feedback-rg" \
  --allowed-origins "https://your-static-web-app-url.azurestaticapps.net"
```

## 🔐 Security Setup (Recommended)

### Create Managed Identity (Advanced)

```bash
# Enable system-assigned managed identity for your web app
az webapp identity assign \
  --name "basf-feedback-api" \
  --resource-group "basf-feedback-rg"

# Grant permissions to Text Analytics resource
az role assignment create \
  --assignee-object-id "your-webapp-principal-id" \
  --role "Cognitive Services User" \
  --scope "/subscriptions/your-subscription-id/resourceGroups/your-cognitive-services-rg/providers/Microsoft.CognitiveServices/accounts/your-text-analytics-resource"
```

## 📊 Monitoring Setup (Optional but Impressive)

### Create Application Insights

```bash
# Create Application Insights resource
az monitor app-insights component create \
  --app "basf-feedback-insights" \
  --location "East US" \
  --resource-group "basf-feedback-rg"

# Get instrumentation key
az monitor app-insights component show \
  --app "basf-feedback-insights" \
  --resource-group "basf-feedback-rg" \
  --query "instrumentationKey" -o tsv
```

### Connect Application Insights to Web App

```bash
# Add Application Insights to your web app
az webapp config appsettings set \
  --name "basf-feedback-api" \
  --resource-group "basf-feedback-rg" \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string"
```

## 🌐 Domain Configuration (Optional)

### Configure Custom Domain

```bash
# Add custom domain to Static Web App (if you have one)
az staticwebapp hostname set \
  --name "basf-feedback-frontend" \
  --resource-group "basf-feedback-rg" \
  --hostname "your-custom-domain.com"
```

## 📝 Important URLs to Save

After setup, save these URLs:

- **Backend API URL**: `https://basf-feedback-api.azurewebsites.net`
- **Frontend URL**: `https://basf-feedback-frontend.azurestaticapps.net`
- **Application Insights**: Available in Azure Portal

## 🔍 Verification Steps

1. **Test Backend**: Visit `https://basf-feedback-api.azurewebsites.net/api/v1/health`
2. **Test Frontend**: Visit your Static Web App URL
3. **Check Logs**: Use Azure Portal or CLI to view application logs
4. **Monitor**: Check Application Insights dashboard

## 🚨 Troubleshooting

### Common Issues:

**Backend not starting:**

```bash
# Check logs
az webapp log tail --name "basf-feedback-api" --resource-group "basf-feedback-rg"
```

**CORS errors:**

```bash
# Update CORS settings
az webapp cors add --name "basf-feedback-api" --resource-group "basf-feedback-rg" --allowed-origins "*"
```

**Environment variables not set:**

```bash
# Verify app settings
az webapp config appsettings list --name "basf-feedback-api" --resource-group "basf-feedback-rg"
```

## 💰 Cost Management

**Free Tier Limits:**

- App Service: 60 minutes/day compute time
- Static Web Apps: 100 GB bandwidth/month
- Application Insights: 1 GB data/month

**Monitor usage:**

```bash
# Check your subscription usage
az consumption usage list --top 10
```

## 🎯 Next Steps

Once you complete this setup:

1. ✅ All Azure resources are created
2. ✅ Environment variables are configured
3. ✅ Monitoring is enabled
4. ✅ CORS is configured

**Now run the deployment scripts to deploy your application!**

---

## 📞 Support

If you encounter issues:

- Check Azure Portal for detailed error messages
- Review Application Insights logs
- Verify all environment variables are set correctly
- Ensure your GitHub repository is accessible

**Total setup time: 30-45 minutes**
**Monthly cost estimate: $0 (using free tiers)**
