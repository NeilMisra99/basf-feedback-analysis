# BASF Feedback Analysis Application

A production-ready, full-stack web application that analyzes customer feedback using Azure AI services for sentiment analysis, intelligent response generation, and emotion-aware text-to-speech synthesis.

## 🚀 Live Demo

- **Frontend**: [Deployed on Azure Static Web Apps](https://your-app.azurestaticapps.net)
- **Backend API**: [Deployed on Azure App Service](https://your-app.azurewebsites.net)

## ✨ Features

- 🎯 **Intelligent Feedback Analysis** - Azure Text Analytics with opinion mining
- 🤖 **AI-Powered Responses** - OpenAI GPT-4o generates contextual replies
- 🎵 **Emotion-Aware Audio** - Azure Speech Services with SSML emotion adaptation
- 📊 **Real-time Dashboard** - Live feedback monitoring with advanced audio controls
- 🛡️ **Production Security** - Managed Identity, input validation, HTTPS enforcement
- 📱 **Responsive Design** - Mobile-first UI with modern React components

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
- Node.js 20 LTS and Python 3.13
- Azure subscription (free tier sufficient)
- API keys: Azure Text Analytics, Azure Speech, OpenAI

### Local Development

1. **Clone and configure**:
   ```bash
   git clone <your-repo-url>
   cd basf-app
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

3. **Start frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access locally**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

## ☁️ Azure Deployment

### One-Time Setup
Follow the detailed [Azure Setup Guide](./AZURE_SETUP_GUIDE.md) to:
- Create Azure resources (App Service, Static Web App)
- Configure environment variables
- Set up monitoring and security

### Deploy to Azure
The application auto-deploys via GitHub Actions when you push to main branch.

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python run.py  # Runs on port 5000
```

### Frontend Development
```bash
cd frontend
npm run dev    # Runs on port 3000 with HMR
npm run build  # Production build
npm run lint   # TypeScript + ESLint checking
```

### API Testing
```bash
# Health check
curl https://your-app.azurewebsites.net/api/v1/health

# Submit feedback
curl -X POST https://your-app.azurewebsites.net/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service!", "category": "service"}'
```

## 📊 Key Technical Highlights

### Performance Optimizations
- **React.memo** and strategic memoization
- **Code splitting** with lazy loading
- **Bundle optimization** with Vite
- **Database indexing** for fast queries

### Security Features
- **Azure Managed Identity** for secure API access
- **Input validation** with XSS protection
- **HTTPS enforcement** in production
- **Environment variable validation**

### Production Architecture
- **Health checks** and monitoring
- **Graceful error handling** with fallbacks
- **Structured logging** for troubleshooting
- **Auto-scaling** with Azure App Service

## 📈 Monitoring & Operations

- **Application Insights** for performance monitoring
- **Health endpoints** for system status
- **Structured logging** for debugging
- **Cost optimization** using Azure free tiers

## 🎯 Technical Excellence

This implementation features:

- ✅ **Enterprise-grade Azure integration** with comprehensive AI services
- ✅ **Modern React performance patterns** with TypeScript
- ✅ **Production-ready Flask architecture** with proper separation
- ✅ **CI/CD pipeline** with GitHub Actions and Azure
- ✅ **Comprehensive error handling** and monitoring
- ✅ **Security best practices** with managed identity
- ✅ **Cost-optimized design** for efficient operations

## 📋 Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Azure Services (Required)
AZURE_TEXT_ANALYTICS_KEY=your-key
AZURE_TEXT_ANALYTICS_ENDPOINT=your-endpoint
AZURE_SPEECH_KEY=your-key
AZURE_SPEECH_REGION=your-region

# OpenAI (Required)
OPENAI_API_KEY=your-key
OPENAI_MODEL=gpt-4o

# Application (Auto-configured for Azure)
REACT_APP_API_URL=https://your-app.azurewebsites.net/api/v1
SECRET_KEY=your-secure-key
```

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd frontend && npm test

# Integration tests
npm run test:e2e
```

## 📚 Documentation

- [Azure Setup Guide](./AZURE_SETUP_GUIDE.md) - Complete deployment walkthrough
- [Architecture Overview](./docs/03-architecture-overview.md) - System design details
- [API Documentation](./docs/08-api-documentation.md) - Endpoint specifications

## 💰 Cost Estimate

**Monthly Azure costs (using free tiers):**
- App Service: $0 (Free tier - 60 min/day)
- Static Web Apps: $0 (Free tier - 100GB bandwidth)
- Text Analytics: $0 (5K transactions/month)
- Speech Services: $0 (5 hours audio/month)

**Total: $0/month for demo usage**

---

## 🏆 Why This Matters

This application represents:
- **Modern Azure ecosystem integration** with Static Web Apps + App Service
- **Production-ready React** with performance optimizations and TypeScript
- **Enterprise Flask patterns** with proper error handling and monitoring  
- **Advanced AI/ML integration** using Azure Cognitive Services and OpenAI
- **DevOps best practices** with GitHub Actions and Infrastructure as Code
- **Cost optimization** and security-first architecture

**Built for Azure, optimized for scale, designed for maintainability.**