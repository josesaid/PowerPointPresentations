#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

LINKEDIN_EMAIL = os.environ.get('LINKEDIN_EMAIL', '')
LINKEDIN_PASSWORD = os.environ.get('LINKEDIN_PASSWORD', '')

def publish_to_linkedin(article_title, article_url, tags):
    """Publish article teaser to LinkedIn"""
    
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        print("ERROR: LinkedIn credentials missing")
        return False
    
    print("Starting LinkedIn automation...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            # 1. Login to LinkedIn
            print("1. Logging in...")
            page.goto('https://www.linkedin.com/login')
            page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
            page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
            page.click('button[type="submit"]')
            
            # Wait for login
            page.wait_for_url('https://www.linkedin.com/feed/**', timeout=30000)
            print("✓ Logged in successfully")
            
            # 2. Click on "Start a post"
            print("2. Opening post composer...")
            time.sleep(2)
            page.click('text=Start a post')
            time.sleep(2)
            
            # 3. Generate teaser in Spanish
            teaser = generate_linkedin_teaser(article_title, article_url, tags)
            print(f"Teaser: {teaser[:100]}...")
            
            # 4. Type content
            print("3. Writing post...")
            page.fill('[contenteditable="true"]', teaser)
            time.sleep(1)
            
            # 5. Publish
            print("4. Publishing...")
            publish_btn = page.locator('button:has-text("Post")')
            publish_btn.click()
            
            # Wait for confirmation
            time.sleep(5)
            
            print("✓ Published to LinkedIn!")
            return True
            
        except Exception as e:
            print(f"✗ LinkedIn error: {e}")
            return False
        finally:
            browser.close()

def generate_linkedin_teaser(title, url, tags):
    """Generate Spanish LinkedIn teaser"""
    tag_str = ' '.join([f'#{tag}' for tag in tags[:3]])
    
    teasers = [
        f"🚀 Nuevo artículo: {title}\n\nConócelos detalles aquí 👇\n{url}\n\n{tag_str}",
        f"📚 Acabo de publicar: {title}\n\nLee el artículo completo:\n{url}\n\n{tag_str}",
        f"💡 Compartiendo mi experiencia con {title}\n\nDetalle: {url}\n\n{tag_str}",
    ]
    
    import hashlib
    seed = int(hashlib.md5(title.encode()).hexdigest(), 16)
    teaser = teasers[seed % len(teasers)]
    
    return teaser[:300]

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 linkedin.py <title> <url> <tags>")
        sys.exit(1)
    
    title = sys.argv[1]
    url = sys.argv[2]
    tags = sys.argv[3].split(',')
    
    success = publish_to_linkedin(title, url, tags)
    sys.exit(0 if success else 1)
