# 🌐 Deployment Guide - AI Stock Market Analyzer

Choose the hosting option that best fits your needs:

## 🎯 **Quick Comparison**

| Platform | Cost | Difficulty | Best For |
|----------|------|------------|----------|
| Streamlit Cloud | Free | ⭐ Easy | Personal projects, demos |
| Railway | $5/month | ⭐⭐ Easy | Small teams, prototypes |
| Digital Ocean | $10/month | ⭐⭐⭐ Medium | Production apps |
| AWS/GCP/Azure | $15-50/month | ⭐⭐⭐⭐ Hard | Enterprise, scalability |
| VPS | $5-20/month | ⭐⭐⭐ Medium | Full control, custom setup |

---

## 🚀 **Option 1: Streamlit Cloud (FREE & EASIEST)**

### Prerequisites:
- GitHub account
- Public repository (or Streamlit Cloud subscription)

### Steps:

#### 1. Prepare Your Repository
```bash
# Create .gitignore
echo "*.db
*.log
.env
__pycache__/
.pytest_cache/
exports/
data/" > .gitignore

# Initialize git and push to GitHub
git init
git add .
git commit -m "Initial commit: AI Stock Market Analyzer"
git remote add origin https://github.com/yourusername/ai-stock-analyzer.git
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Repository: `yourusername/ai-stock-analyzer`
5. Branch: `main`
6. Main file path: `app.py`
7. Click "Deploy!"

#### 3. Configure Environment Variables
In your Streamlit Cloud app dashboard:
1. Go to Settings → Secrets
2. Add your API keys:

```toml
NEWSAPI_KEY = "your_newsapi_key_here"
FINNHUB_KEY = "your_finnhub_key_here"
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token_here"
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
FROM_EMAIL = "your_email@gmail.com"
```

#### 4. Access Your App
- Your app will be available at: `https://yourappname.streamlit.app`
- Auto-deploys on every GitHub push
- Free SSL certificate included

---

## 🛠️ **Option 2: Railway (EASY & AFFORDABLE)**

### Cost: $5/month for hobby plan

#### 1. Prepare for Railway
```bash
# Install Railway CLI
npm install -g @railway/cli
# or
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login
```

#### 2. Create railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "streamlit run app.py --server.port=$PORT --server.address=0.0.0.0",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 3. Deploy
```bash
# Initialize Railway project
railway init

# Set environment variables
railway variables set NEWSAPI_KEY=your_key_here
railway variables set FINNHUB_KEY=your_key_here
railway variables set TWITTER_BEARER_TOKEN=your_token_here
railway variables set EMAIL_USER=your_email@gmail.com
railway variables set EMAIL_PASSWORD=your_app_password

# Deploy
railway up
```

---

## 🐳 **Option 3: Digital Ocean App Platform**

### Cost: $10-25/month

#### 1. Create App Spec
Create `.do/app.yaml`:
```yaml
name: ai-stock-analyzer
services:
- name: web
  source_dir: /
  github:
    repo: yourusername/ai-stock-analyzer
    branch: main
  run_command: streamlit run app.py --server.port=8080 --server.address=0.0.0.0
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
  envs:
  - key: NEWSAPI_KEY
    scope: RUN_TIME
    type: SECRET
  - key: FINNHUB_KEY
    scope: RUN_TIME
    type: SECRET
  - key: TWITTER_BEARER_TOKEN
    scope: RUN_TIME
    type: SECRET
  - key: EMAIL_USER
    scope: RUN_TIME
    type: SECRET
  - key: EMAIL_PASSWORD
    scope: RUN_TIME
    type: SECRET
```

#### 2. Deploy via Web Interface
1. Visit [cloud.digitalocean.com/apps](https://cloud.digitalocean.com/apps)
2. Create → Apps → GitHub
3. Select your repository
4. Configure environment variables in the web UI
5. Deploy

---

## ☁️ **Option 4: AWS Elastic Beanstalk**

### Cost: $15-50/month (varies by usage)

#### 1. Prepare for AWS
```bash
# Install AWS CLI and EB CLI
pip install awscli awsebcli

# Configure AWS credentials
aws configure
```

#### 2. Create .ebextensions/python.config
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.py
  aws:elasticbeanstalk:application:environment:
    STREAMLIT_SERVER_PORT: 8501
    STREAMLIT_SERVER_ADDRESS: 0.0.0.0
```

#### 3. Deploy
```bash
# Initialize EB application
eb init -p python-3.11 ai-stock-analyzer

# Create environment
eb create ai-stock-analyzer-env

# Set environment variables
eb setenv NEWSAPI_KEY=your_key FINNHUB_KEY=your_key TWITTER_BEARER_TOKEN=your_token

# Deploy
eb deploy
```

---

## 🖥️ **Option 5: VPS (Full Control)**

### Recommended: Ubuntu 22.04 VPS ($5-20/month)

#### 1. Server Setup
```bash
# Connect to your VPS
ssh root@your_server_ip

# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y
```

#### 2. Deploy Application
```bash
# Clone your repository
git clone https://github.com/yourusername/ai-stock-analyzer.git
cd ai-stock-analyzer

# Create .env file
nano .env
# Add your API keys

# Start application
docker-compose up -d

# Set up reverse proxy (optional)
# Install nginx
apt install nginx -y

# Configure nginx
nano /etc/nginx/sites-available/ai-stock-analyzer
```

#### 3. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### 4. Enable Site & SSL
```bash
# Enable site
ln -s /etc/nginx/sites-available/ai-stock-analyzer /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

# Install SSL with Let's Encrypt
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your_domain.com
```

---

## 🔧 **Option 6: Docker Local Testing**

### For Development & Testing

```bash
# Build and run locally
docker-compose up --build

# Access at http://localhost:8501

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 🔐 **Security Considerations**

### Environment Variables
Never commit API keys to Git:
```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets.*" >> .gitignore
```

### Production Security
1. **Use HTTPS**: Always enable SSL/TLS
2. **Environment Variables**: Use platform secrets management
3. **Firewall**: Restrict access to necessary ports only
4. **Updates**: Keep dependencies updated
5. **Monitoring**: Set up logging and alerts

---

## 📊 **Monitoring & Maintenance**

### Health Checks
The application includes health check endpoints:
- `http://your-app/_stcore/health` - Streamlit health
- Custom health check in Docker

### Logging
Enable logging for production:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### Updates
For automatic updates (Streamlit Cloud):
```bash
git add .
git commit -m "Update: feature description"
git push origin main
# Streamlit Cloud auto-deploys
```

---

## 🎯 **Recommended Deployment Path**

### For Beginners:
1. **Start with Streamlit Cloud** (free, easy)
2. **Move to Railway** when you need more control
3. **Upgrade to VPS** for production use

### For Businesses:
1. **Start with Railway/Digital Ocean** (reliable, affordable)
2. **Scale to AWS/GCP/Azure** for enterprise needs

### For Developers:
1. **Local Docker** for development
2. **VPS with Docker** for full control
3. **Cloud platforms** for scaling

---

## 🆘 **Troubleshooting**

### Common Issues:

#### Port Issues
```bash
# Change port in Streamlit
streamlit run app.py --server.port=8080
```

#### Memory Issues
```bash
# Increase Docker memory
docker run -m 1g your-image
```

#### Environment Variables Not Loading
```bash
# Check if .env exists
ls -la .env

# Test environment loading
python -c "import os; print(os.getenv('NEWSAPI_KEY'))"
```

#### Build Failures
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

---

## 🎉 **You're Ready to Deploy!**

Choose your preferred option and follow the steps above. Your AI Stock Market Analyzer will be live and accessible to users worldwide!

### Quick Start Recommendations:
- **First time hosting?** → Streamlit Cloud
- **Need custom domain?** → Railway
- **Building a business?** → Digital Ocean
- **Enterprise scale?** → AWS/GCP/Azure

**Happy Hosting! 🚀**