# 🚀 BASF Feedback Analysis Application

A full-stack web application that analyzes customer feedback using Azure AI services for sentiment analysis, intelligent response generation, and emotion-aware text-to-speech synthesis.

## ✨ Features

- 📝 **Feedback Submission** - Simple form for collecting customer feedback
- 🎯 **Sentiment Analysis** - Azure Text Analytics processes feedback to determine positive, negative, or neutral sentiment
- 🤖 **AI-Powered Responses** - OpenAI GPT-4 generates contextual, sentiment-appropriate responses
- 🎵 **Emotion-Aware Audio** - Azure Speech Services creates audio responses with emotion-based voice styles
- 📊 **Interactive Dashboard** - View all feedback with sentiment scores, AI responses, and audio playback
- 📱 **Responsive Design** - Modern React UI that works on desktop and mobile

## 🏗️ Architecture

### Frontend

- **React 19** with TypeScript for type safety
- **Vite** for fast development and optimized builds
- **Tailwind CSS** with shadcn/ui components
- **Advanced audio management** with global state

### Backend

- **Flask** with production-grade architecture
- **Azure Text Analytics SDK** with opinion mining
- **OpenAI Python SDK** with GPT-4o integration
- **Azure Speech Services** with SSML emotion synthesis
- **SQLAlchemy ORM** with SQLite database

### Cloud Infrastructure

- **Azure Static Web Apps** for frontend hosting
- **Azure App Service** for backend API
- **GitHub Actions** for CI/CD pipeline
- **Application Insights** for monitoring

## 🚀 Quick Setup

### Prerequisites

- **Node.js 20 LTS** and **Python 3.13**
- **Azure subscription** (free tier sufficient)
- **API keys**: Azure Text Analytics, Azure Speech, OpenAI

### 🔑 Step 1: Get API Keys

#### Azure Services Setup

You'll need **two Azure resource groups**:

**Resource Group 1: Core Services**

- Contains: App Service, Static Web App, App Service Plan
- Use for: Application hosting and deployment

**Resource Group 2: AI Services**

- Contains: Language Service (Text Analytics), Speech Service
- Use for: AI processing

#### Create Azure Language Service (Text Analytics)

1. **Sign in** to [Azure Portal](https://portal.azure.com)
2. **Click** "Create a resource" → Search "Language service"
3. **Configure**:
   - **Resource Group**: Create new `feedback-analysis-ai-rg`
   - **Region**: Choose closest to you (e.g., "East US")
   - **Name**: `feedback-analysis-language`
   - **Pricing**: Free F0 (5,000 text records/month)
4. **Get credentials**: Go to resource → "Keys and Endpoint"
   - Save `KEY 1` and `Endpoint URL`

#### Create Azure Speech Service

1. **Create resource** → Search "Speech service"
2. **Configure**:
   - **Resource Group**: Use existing `feedback-analysis-ai-rg`
   - **Region**: Same as Language Service
   - **Name**: `feedback-analysis-speech`
   - **Pricing**: Free F0 (5 hours audio/month)
3. **Get credentials**: Go to resource → "Keys and Endpoint"
   - Save `KEY 1` and `Location/Region`

#### OpenAI API Setup

1. **Sign up** at [OpenAI Platform](https://platform.openai.com/signup)
2. **Add payment method** (required for API access)
3. **Create API key**:
   - Go to [API Keys](https://platform.openai.com/api-keys)
   - Click "Create new secret key"
   - Name: "Feedback Analysis App"
   - **Save the key** (starts with `sk-`)
4. **Set spending limit**: $10/month recommended for demo

### 🔧 Step 2: Configure Environment

1. **Clone repository**:

   ```bash
   git clone <your-repo-url>
   cd basf-app
   ```

2. **Create environment file**:

   ```bash
   cp .env.example .env
   ```

3. **Edit** `.env` with your API keys:

   ```bash
   # Azure Text Analytics
   AZURE_TEXT_ANALYTICS_ENDPOINT=https://feedback-analysis-language.cognitiveservices.azure.com/
   AZURE_TEXT_ANALYTICS_KEY=your_text_analytics_key_here

   # Azure Speech Services
   AZURE_SPEECH_KEY=your_speech_key_here
   AZURE_SPEECH_REGION=eastus

   # OpenAI
   OPENAI_API_KEY=sk-your_openai_key_here
   OPENAI_MODEL=gpt-4o
   ```

### 🏃‍♂️ Step 3: Run the Application

#### Option A: Start Both Services Separately

**Terminal 1 - Backend**:

```bash
cd backend
pip install -r requirements.txt
python application.py
```

**Terminal 2 - Frontend**:

```bash
cd frontend
npm install
npm run dev
```

#### Option B: Using Development Script at root

```bash
./dev.sh
```

### 🌐 Step 4: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5001
- **Health Check**: http://localhost:5001/api/v1/health

## 🧪 Test Your Setup

### 1\. Test Application

1. **Submit feedback**: Go to http://localhost:3000
2. **Enter text**: "This product is amazing!"
3. **Check processing**: Should show "Processing..." initially
4. **View results**: Sentiment analysis, AI response, and audio file
5. **Play audio**: Click play button to hear emotion-based response

## ☁️ Azure Deployment (Production)

Deploy your application to Azure using Static Web Apps (frontend) + App Service (backend) with automated GitHub Actions.

### 🏗️ Step 1: Create Hosting Infrastructure

Now create a **new resource group** for hosting your application (your AI services are already set up):

**Create App Service Plan:**

1. **Azure Portal** → "Create resource" → "App Service Plan"
2. **Configure**:
   - **Resource Group**: Create new `feedback-analysis-rg`
   - **Name**: `feedback-analysis-plan`
   - **Region**: Eg: East US (same as your AI services)
   - **Pricing**: Free F1 tier (sufficient for demo)

**Create App Service (Backend API):**

1. **Create resource** → "Web App"
2. **Configure**:
   - **Resource Group**: `feedback-analysis-rg`
   - **Name**: `basf-feedback-api` (must be globally unique)
   - **Runtime**: Python 3.13
   - **Region**: Eg: East US
   - **App Service Plan**: Use existing `feedback-analysis-plan`

**Create Static Web App (Frontend):**

1. **Create resource** → "Static Web Apps"
2. **Configure**:
   - **Resource Group**: `feedback-analysis-rg`
   - **Name**: `basf-feedback-frontend`
   - **Plan**: Free tier
   - **Source**: GitHub (connect to your repository)
   - **Build Details**:
     - **Framework**: React
     - **App location**: `/frontend`
     - **Output location**: `dist`

### 🔧 Step 2: Configure App Service Environment Variables

In your **App Service** → Configuration → Application Settings, add these **exactly**:

```bash
# Azure AI Services
AZURE_TEXT_ANALYTICS_ENDPOINT=https://feedback-analysis-language.cognitiveservices.azure.com/
AZURE_TEXT_ANALYTICS_KEY=your_language_service_key_here
AZURE_SPEECH_KEY=your_speech_service_key_here
AZURE_SPEECH_REGION=eastus

# OpenAI
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_MODEL=gpt-4o

# App Configuration
SECRET_KEY=your-secure-production-secret-key-here
FLASK_ENV=production
SCM_DO_BUILD_DURING_DEPLOYMENT=1
CORS_ORIGINS=https://basf-feedback-frontend.azurestaticapps.net
```

**⚠️ Important**: Replace `basf-feedback-frontend` with your actual Static Web App name.

### 🔑 Step 3: Configure GitHub Secrets

In your **GitHub repository** → Settings → Secrets and variables → Actions, add:

#### Backend Deployment Secrets:

1. **AZURE_BACKEND_APP_NAME**
   - Value: `basf-feedback-api` (your App Service name)

2. **AZURE_BACKEND_PUBLISH_PROFILE**
   - Go to App Service → Overview → "Get publish profile"
   - Copy entire XML content as secret value

#### Frontend Deployment Secrets:

1. **AZURE_STATIC_WEB_APPS_API_TOKEN**
   - Go to Static Web App → Overview → "Manage deployment token"
   - Copy the deployment token

2. **REACT_APP_API_URL**
   - Value: `https://basf-feedback-api.azurewebsites.net/api/v1`
   - Replace `basf-feedback-api` with your App Service name

### 🚀 Step 4: Deploy via GitHub Actions

Your application will automatically deploy when you push to the main branch:

**Frontend**: Triggers on changes to `/frontend/` folder **Backend**: Triggers on changes to `/backend/` folder

#### Manual Deployment:

1. Go to **GitHub** → Actions tab
2. Select workflow (Frontend or Backend)
3. Click "Run workflow"

### ✅ Step 5: Verify Deployment

#### Test Backend API:

```bash
# Health check
curl https://basf-feedback-api.azurewebsites.net/api/v1/health

# Expected response: {"status": "healthy", ...}
```

#### Test Frontend:

- Visit: `https://basf-feedback-frontend.azurestaticapps.net`
- Submit feedback to test end-to-end flow

#### Test Full Integration:

1. **Submit feedback** through your deployed frontend
2. **Verify processing** - should show "Processing..." then complete
3. **Check dashboard** - sentiment, AI response, and audio should appear
4. **Play audio** - emotion-based voice should work

### 🔧 Environment Variables Reference

Our `.env.example` shows the complete structure:

**Local Development:**

```bash
# Uses .env.local or .env file
AZURE_TEXT_ANALYTICS_KEY=your-key
REACT_APP_API_URL=http://localhost:5001/api/v1
```

**Production (Azure App Service):**

```bash
# Set in Azure Portal → App Service → Configuration
AZURE_TEXT_ANALYTICS_KEY=your-key
CORS_ORIGINS=https://your-static-web-app.azurestaticapps.net
```

**GitHub Actions:**

```bash
# Set in GitHub → Settings → Secrets
AZURE_BACKEND_PUBLISH_PROFILE=<xml-content>
REACT_APP_API_URL=https://your-app-service.azurewebsites.net/api/v1
```

### 🚨 Troubleshooting Deployment

**"CORS error" in production:**

- Update `CORS_ORIGINS` in App Service configuration
- Ensure it matches your Static Web App URL exactly

**"Environment variables not found":**

- Check App Service → Configuration → Application Settings
- Verify all required variables are set
- Restart App Service after adding variables

**"GitHub Actions failing":**

- Verify all 4 GitHub secrets are set correctly
- Check Actions tab for detailed error logs
- Ensure publish profile is complete XML content

**"Static Web App not updating":**

- Check deployment status in Azure Portal
- Verify GitHub connection is active
- Check build logs in GitHub Actions
