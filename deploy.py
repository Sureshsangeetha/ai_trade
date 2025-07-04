#!/usr/bin/env python3
"""
Automated deployment script for AI Stock Market Analyzer
Helps deploy to various cloud platforms with guided setup.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, check=True):
    """Run shell command and return result"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr

def check_requirements():
    """Check if basic requirements are met"""
    print("🔍 Checking requirements...")
    
    # Check if git is available
    stdout, stderr = run_command("git --version", check=False)
    if "git version" not in stdout:
        print("❌ Git is required but not found. Please install Git first.")
        return False
    
    # Check if we're in a git repository
    stdout, stderr = run_command("git status", check=False)
    if "not a git repository" in stderr:
        print("⚠️ Not in a Git repository. Will initialize one.")
    
    print("✅ Basic requirements check passed")
    return True

def create_gitignore():
    """Create .gitignore file"""
    gitignore_content = """# Environment variables
.env
*.key
secrets.*

# Database files
*.db
*.sqlite3

# Logs
*.log
logs/

# Cache
__pycache__/
.pytest_cache/
.cache/

# IDE
.vscode/
.idea/

# Output directories
exports/
data/
reports/

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    print("✅ Created .gitignore file")

def setup_git_repository():
    """Initialize git repository and prepare for deployment"""
    print("\n📁 Setting up Git repository...")
    
    # Check if already a git repo
    stdout, stderr = run_command("git status", check=False)
    if "not a git repository" in stderr:
        run_command("git init")
        print("✅ Initialized Git repository")
    
    # Create .gitignore
    if not os.path.exists('.gitignore'):
        create_gitignore()
    
    # Add files
    run_command("git add .")
    
    # Check if there are changes to commit
    stdout, stderr = run_command("git status --porcelain", check=False)
    if stdout:
        run_command('git commit -m "Prepare for deployment: AI Stock Market Analyzer"')
        print("✅ Committed changes to Git")
    else:
        print("✅ No changes to commit")

def deploy_streamlit_cloud():
    """Guide user through Streamlit Cloud deployment"""
    print("\n🚀 Deploying to Streamlit Cloud...")
    
    # Check if remote exists
    stdout, stderr = run_command("git remote -v", check=False)
    if not stdout:
        print("\n📝 GitHub Repository Setup:")
        print("1. Go to https://github.com/new")
        print("2. Create a new repository named 'ai-stock-analyzer'")
        print("3. Make it public (required for free Streamlit Cloud)")
        
        username = input("\nEnter your GitHub username: ")
        repo_url = f"https://github.com/{username}/ai-stock-analyzer.git"
        
        run_command(f"git remote add origin {repo_url}")
        print(f"✅ Added remote: {repo_url}")
    
    # Push to GitHub
    print("\n📤 Pushing to GitHub...")
    stdout, stderr = run_command("git push -u origin main", check=False)
    if "fatal" in stderr:
        print("⚠️ Push failed. Make sure your GitHub repository exists and is accessible.")
        print("You may need to:")
        print("1. Create the repository on GitHub")
        print("2. Set up authentication (SSH keys or personal access token)")
    else:
        print("✅ Code pushed to GitHub")
    
    print("\n🌐 Streamlit Cloud Deployment:")
    print("1. Visit https://share.streamlit.io")
    print("2. Sign in with GitHub")
    print("3. Click 'New app'")
    print("4. Select your repository")
    print("5. Set main file path: app.py")
    print("6. Click 'Deploy!'")
    
    print("\n🔐 Environment Variables Setup:")
    print("In your Streamlit Cloud app dashboard, go to Settings → Secrets and add:")
    
    secrets_template = """NEWSAPI_KEY = "your_newsapi_key_here"
FINNHUB_KEY = "your_finnhub_key_here"
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token_here"
EMAIL_USER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_gmail_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = "587"
FROM_EMAIL = "your_email@gmail.com"
"""
    
    print(secrets_template)

def deploy_railway():
    """Guide user through Railway deployment"""
    print("\n🛠️ Deploying to Railway...")
    
    # Check if Railway CLI is installed
    stdout, stderr = run_command("railway --version", check=False)
    if "railway version" not in stdout:
        print("📦 Installing Railway CLI...")
        install_cmd = input("Choose installation method:\n1. npm (y/n): ")
        if install_cmd.lower() == 'y':
            run_command("npm install -g @railway/cli")
        else:
            print("Please install Railway CLI manually:")
            print("curl -fsSL https://railway.app/install.sh | sh")
            return
    
    # Login to Railway
    print("🔐 Please login to Railway...")
    run_command("railway login")
    
    # Create railway.json
    railway_config = {
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
    
    with open('railway.json', 'w') as f:
        json.dump(railway_config, f, indent=2)
    print("✅ Created railway.json")
    
    # Initialize Railway project
    run_command("railway init")
    
    # Set environment variables
    print("\n🔧 Setting environment variables...")
    env_vars = [
        "NEWSAPI_KEY",
        "FINNHUB_KEY", 
        "TWITTER_BEARER_TOKEN",
        "EMAIL_USER",
        "EMAIL_PASSWORD"
    ]
    
    for var in env_vars:
        value = input(f"Enter {var}: ")
        if value:
            run_command(f'railway variables set {var}="{value}"')
    
    # Deploy
    print("\n🚀 Deploying to Railway...")
    run_command("railway up")
    print("✅ Deployed to Railway!")

def deploy_docker_local():
    """Build and run Docker container locally"""
    print("\n🐳 Building Docker container...")
    
    # Check if Docker is available
    stdout, stderr = run_command("docker --version", check=False)
    if "Docker version" not in stdout:
        print("❌ Docker is required but not found. Please install Docker first.")
        return
    
    # Build Docker image
    print("🔨 Building Docker image...")
    run_command("docker build -t ai-stock-analyzer .")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("# Add your API keys here\n")
            f.write("NEWSAPI_KEY=your_newsapi_key_here\n")
            f.write("FINNHUB_KEY=your_finnhub_key_here\n")
            f.write("TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here\n")
            f.write("EMAIL_USER=your_email@gmail.com\n")
            f.write("EMAIL_PASSWORD=your_gmail_app_password\n")
        print("✅ Created .env template. Please edit it with your API keys.")
    
    # Run with docker-compose
    print("🚀 Starting application with Docker Compose...")
    run_command("docker-compose up -d")
    print("✅ Application running at http://localhost:8501")

def main():
    """Main deployment function"""
    print("🌐 AI Stock Market Analyzer - Deployment Tool")
    print("=" * 50)
    
    if not check_requirements():
        sys.exit(1)
    
    setup_git_repository()
    
    print("\n🎯 Choose deployment option:")
    print("1. Streamlit Cloud (Free, easiest)")
    print("2. Railway ($5/month, easy)")
    print("3. Docker Local (development)")
    print("4. Manual setup (see DEPLOYMENT_GUIDE.md)")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        deploy_streamlit_cloud()
    elif choice == "2":
        deploy_railway()
    elif choice == "3":
        deploy_docker_local()
    elif choice == "4":
        print("\n📖 Please follow the instructions in DEPLOYMENT_GUIDE.md")
        print("Available at: https://github.com/yourusername/ai-stock-analyzer/blob/main/DEPLOYMENT_GUIDE.md")
    else:
        print("❌ Invalid choice. Please run the script again.")
        sys.exit(1)
    
    print("\n🎉 Deployment process completed!")
    print("\n📚 Next steps:")
    print("1. Set up your API keys in the platform's environment variables")
    print("2. Test your deployed application")
    print("3. Configure custom domain if needed")
    print("4. Set up monitoring and alerts")

if __name__ == "__main__":
    main()