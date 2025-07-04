#!/usr/bin/env python3
"""
Quick fix script for Streamlit Cloud deployment issues.
Switches to the streamlined version optimized for cloud deployment.
"""

import os
import shutil

def main():
    print("🛠️ AI Stock Market Analyzer - Deployment Fix")
    print("=" * 50)
    
    print("This script will:")
    print("1. Backup your current app.py to app_full.py")
    print("2. Switch to the streamlined version (app_streamlit.py)")
    print("3. Update requirements.txt for cloud compatibility")
    print()
    
    proceed = input("Do you want to proceed? (y/n): ").lower()
    
    if proceed != 'y':
        print("Cancelled.")
        return
    
    try:
        # Backup current app if it exists
        if os.path.exists('app.py'):
            if os.path.exists('app_full.py'):
                print("⚠️ app_full.py already exists. Skipping backup.")
            else:
                shutil.move('app.py', 'app_full.py')
                print("✅ Backed up app.py to app_full.py")
        
        # Switch to streamlined version
        if os.path.exists('app_streamlit.py'):
            shutil.copy('app_streamlit.py', 'app.py')
            print("✅ Switched to streamlined app (app_streamlit.py -> app.py)")
        else:
            print("❌ app_streamlit.py not found. Cannot switch.")
            return
        
        # Update requirements if streamlit version exists
        if os.path.exists('requirements-streamlit.txt'):
            if os.path.exists('requirements_full.txt'):
                print("⚠️ requirements_full.txt already exists. Skipping backup.")
            else:
                if os.path.exists('requirements.txt'):
                    shutil.move('requirements.txt', 'requirements_full.txt')
                    print("✅ Backed up requirements.txt to requirements_full.txt")
            
            shutil.copy('requirements-streamlit.txt', 'requirements.txt')
            print("✅ Updated requirements.txt for cloud compatibility")
        
        print()
        print("🎉 Deployment fix complete!")
        print()
        print("Next steps:")
        print("1. Test locally: streamlit run app.py")
        print("2. Commit and push to GitHub:")
        print("   git add .")
        print("   git commit -m 'Fix: Streamlined app for Streamlit Cloud'")
        print("   git push origin main")
        print("3. Your Streamlit Cloud app should now deploy successfully!")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")

if __name__ == "__main__":
    main()