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

- **Azure Container Apps** for scalable backend API hosting
- **Azure Container Registry** for Docker image management
- **Azure Blob Storage** for persistent audio file storage
- **Azure Static Web Apps** for frontend hosting
- **GitHub Actions** for automated CI/CD deployment

## 🚀 Quick Setup

### Prerequisites

- **Node.js 20 LTS** and **Python 3.13**
- **Azure subscription** (free tier sufficient)
- **API keys**: Azure Text Analytics, Azure Speech, OpenAI

### 🔑 Step 1: Get API Keys

#### Azure Services Setup

You'll need **two Azure resource groups**:

**Resource Group 1: Core Services**

- Contains: Container Apps, Container Registry, Storage Account, Static Web App
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
   cp .env.example .env.local
   ```

3. **Edit** `.env.local` with your API keys:

   ```bash
   # Azure Text Analytics
   AZURE_TEXT_ANALYTICS_ENDPOINT=https://feedback-analysis-language.cognitiveservices.azure.com/
   AZURE_TEXT_ANALYTICS_KEY=your_text_analytics_key_here

   # Azure Speech Services
   AZURE_SPEECH_KEY=your_speech_key_here
   AZURE_SPEECH_REGION=eastus

   # Azure Storage (for local development with Blob Storage)
   AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...

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

> **Note**: Audio files are automatically uploaded to Azure Blob Storage in production for persistent, scalable storage.

## 🧪 Test Your Setup

### 1\. Test Application

1. **Submit feedback**: Go to http://localhost:3000
2. **Enter text**: "This product is amazing!"
3. **Check processing**: Should show "Processing..." initially
4. **View results**: Sentiment analysis, AI response, and audio file
5. **Play audio**: Click play button to hear emotion-based response

## ☁️ Azure Deployment (Production)

Deploy your application to Azure using **Container Apps** (backend) + **Static Web Apps** (frontend) + **Blob Storage** (audio files) with automated GitHub Actions.

### 🏗️ Step 1: Create Azure Infrastructure

Create a **new resource group** for hosting your application (your AI services are already set up):

**Create Container Registry:**

1. **Azure Portal** → "Create resource" → "Container Registry"
2. **Configure**:
   - **Resource Group**: Create new `feedback-analysis-rg`
   - **Registry name**: `basffeedbackregistry` (must be globally unique)
   - **Location**: East US (same as your AI services)
   - **SKU**: Basic (sufficient for demo)
3. **Enable Admin user**: Settings → Access keys → Admin user (Enable)

**Create Storage Account:**

1. **Create resource** → "Storage account"
2. **Configure**:
   - **Resource Group**: `feedback-analysis-rg`
   - **Storage account name**: `basffeedbackstorage` (must be globally unique)
   - **Region**: East US
   - **Performance**: Standard
   - **Redundancy**: LRS (Locally-redundant storage)
3. **Get connection string**: Access keys → Show keys → Connection string

**Create Container Apps Environment:**

1. **Create resource** → "Container Apps Environment"
2. **Configure**:
   - **Resource Group**: `feedback-analysis-rg`
   - **Environment name**: `basf-feedback-env`
   - **Region**: East US

**Create Container App:**

1. **Create resource** → "Container App"
2. **Configure**:
   - **Resource Group**: `feedback-analysis-rg`
   - **Container app name**: `basf-feedback-api`
   - **Environment**: Use existing `basf-feedback-env`
   - **Container image**: Use quickstart image initially (we'll update via GitHub Actions)
   - **Ingress**: Enabled, HTTP traffic from anywhere, Target port: 5001

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

### 🔧 Step 2: Configure Container App Environment Variables

In your **Container App** → Settings → Environment variables, add these (will be overridden by GitHub Actions):

```bash
# Azure AI Services
AZURE_TEXT_ANALYTICS_ENDPOINT=https://feedback-analysis-language.cognitiveservices.azure.com/
AZURE_TEXT_ANALYTICS_KEY=your_language_service_key_here
AZURE_SPEECH_KEY=your_speech_service_key_here
AZURE_SPEECH_REGION=eastus

# Azure Storage (for audio files)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=basffeedbackstorage;AccountKey=your_storage_key;EndpointSuffix=core.windows.net

# OpenAI
OPENAI_API_KEY=sk-your_openai_key_here
OPENAI_MODEL=gpt-4o

# App Configuration
SECRET_KEY=your-secure-production-secret-key-here
FLASK_ENV=production
CORS_ORIGINS=https://basf-feedback-frontend.azurestaticapps.net
```

**⚠️ Important**: Replace with your actual service names and get the storage connection string from Storage Account → Access keys.

### 🔑 Step 3: Configure GitHub Secrets

In your **GitHub repository** → Settings → Secrets and variables → Actions, add:

#### Container Registry Secrets:

1. **REGISTRY_LOGIN_SERVER** - Your Container Registry login server (e.g., `yourregistry-xxxxx.azurecr.io`)
2. **REGISTRY_USERNAME** - Your Container Registry username (from Access keys)
3. **REGISTRY_PASSWORD** - Your Container Registry password (from Access keys)

#### Azure Deployment Secrets:

1. **AZURE_CREDENTIALS** - Service Principal JSON for Container Apps deployment
2. **AZURE_STORAGE_CONNECTION_STRING** - Storage account connection string

#### Application Environment Secrets:

1. **AZURE_TEXT_ANALYTICS_KEY** - Your Text Analytics key
2. **AZURE_TEXT_ANALYTICS_ENDPOINT** - Your Text Analytics endpoint
3. **AZURE_SPEECH_KEY** - Your Speech service key
4. **AZURE_SPEECH_REGION** - Your Speech service region
5. **OPENAI_API_KEY** - Your OpenAI API key
6. **OPENAI_MODEL** - `gpt-4o`
7. **SECRET_KEY** - Secure random string for Flask
8. **CORS_ORIGINS** - Your Static Web App URL

#### Frontend Deployment:

1. **AZURE_STATIC_WEB_APPS_API_TOKEN** - Static Web App deployment token
2. **REACT_APP_API_URL** - `https://basf-feedback-api.azurecontainerapps.io/api/v1`

**⚠️ Note**: Your Container App URL format is `https://[app-name].[random-string].[region].azurecontainerapps.io`

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
curl https://basf-feedback-api.[random-string].[region].azurecontainerapps.io/api/v1/health

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
