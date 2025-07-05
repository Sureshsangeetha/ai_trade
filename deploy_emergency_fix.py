#!/usr/bin/env python3
"""
Emergency Deployment Fix for Streamlit Cloud
This script will backup your current files and replace them with ultra-minimal versions
"""

import os
import shutil
from datetime import datetime

def backup_and_replace():
    """Backup current files and replace with ultra-minimal versions"""
    
    print("🚨 EMERGENCY DEPLOYMENT FIX")
    print("=" * 50)
    
    # Create backup directory
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Files to backup and replace
    files_to_backup = [
        "app.py",
        "requirements.txt"
    ]
    
    # Backup existing files
    print("\n1. Backing up existing files...")
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))
            print(f"   ✅ Backed up: {file}")
        else:
            print(f"   ⚠️  File not found: {file}")
    
    # Replace with ultra-minimal versions
    print("\n2. Replacing with ultra-minimal versions...")
    
    # Replace app.py
    if os.path.exists("app_ultra_minimal.py"):
        shutil.copy2("app_ultra_minimal.py", "app.py")
        print("   ✅ Replaced app.py with ultra-minimal version")
    else:
        print("   ❌ app_ultra_minimal.py not found!")
    
    # Replace requirements.txt
    if os.path.exists("requirements-ultra-minimal.txt"):
        shutil.copy2("requirements-ultra-minimal.txt", "requirements.txt")
        print("   ✅ Replaced requirements.txt with ultra-minimal version")
    else:
        print("   ❌ requirements-ultra-minimal.txt not found!")
    
    print(f"\n3. Files backed up to: {backup_dir}")
    print("\n4. NEXT STEPS:")
    print("   1. Commit these changes to your GitHub repository")
    print("   2. Push to GitHub")
    print("   3. Your Streamlit Cloud app should now deploy successfully!")
    print("   4. Once working, you can gradually add features back")
    
    print("\n✅ Emergency fix complete!")
    print("🚀 Your app should now work on Streamlit Cloud!")

if __name__ == "__main__":
    backup_and_replace()