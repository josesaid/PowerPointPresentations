#!/usr/bin/env python3
import os
import json
import subprocess
import random
from datetime import datetime

print("=== PUBLISHING PIPELINE START ===\n")

# 1. SELECT RANDOM TOPIC
print("1. Selecting random topic...")
try:
    with open('temas_post_LinkedIn.txt', 'r') as f:
        topics = [t.strip() for t in f.readlines() if t.strip()]
    
    with open('temas_post_LinkedIn_usados.txt', 'r') as f:
        used = [t.strip() for t in f.readlines() if t.strip()]
except:
    used = []

available = [t for t in topics if t not in used]
if not available:
    print("ERROR: No available topics")
    exit(1)

topic = random.choice(available)
print(f"✓ Selected: {topic}\n")

# 2. CHECK API KEYS
print("2. Checking API keys...")
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DEVTO_KEY = os.environ.get('DEVTO_API_KEY', '')

if not ANTHROPIC_KEY or not DEVTO_KEY:
    print("ERROR: Missing API keys")
    exit(1)

print(f"✓ ANTHROPIC_API_KEY: {len(ANTHROPIC_KEY)} chars")
print(f"✓ DEVTO_API_KEY: {len(DEVTO_KEY)} chars\n")

# 3. GENERATE ARTICLE
print("3. Generating article with Claude...")
import urllib.request

prompt = f"""Write a professional technical blog post about: "{topic}"

Format EXACTLY like this:
TITLE: [Article Title]
TAGS: tag1,tag2,tag3,tag4
BODY:
[Markdown content]
END_BODY"""

try:
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps({
            'model': 'claude-opus-4-8',
            'max_tokens': 2000,
            'messages': [{'role': 'user', 'content': prompt}]
        }).encode(),
        headers={
            'x-api-key': ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
    )
    
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        text = data['content'][0]['text'].strip()
        
        # Parse
        lines = text.split('\n')
        title, tags, body = '', [], ''
        parsing_body = False
        
        for line in lines:
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('TAGS:'):
                tags = [t.strip() for t in line.replace('TAGS:', '').split(',')]
            elif line.startswith('BODY:'):
                parsing_body = True
            elif line.startswith('END_BODY'):
                parsing_body = False
            elif parsing_body:
                body += line + '\n'
        
        title = f"{title} ({datetime.now().strftime('%Y-%m-%d %H:%M')})" if title else 'Untitled'
        tags = tags or ['java', 'programming']
        body = body.strip() or f'# {title}\n\nAuto-generated article'
        
        # Clean tags
        cleaned = []
        for tag in tags:
            clean = tag.replace('-', '').replace('_', '').lower()[:20]
            if clean and clean.isalnum():
                cleaned.append(clean)
        tags = cleaned[:4] or ['java', 'programming']
        
        print(f"✓ Generated: {title[:50]}...")
        print(f"✓ Tags: {', '.join(tags)}\n")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

# 4. PUBLISH TO DEV.TO
print("4. Publishing to dev.to...")
payload = {
    'article': {
        'title': title,
        'body_markdown': body,
        'published': True,
        'tags': tags
    }
}

try:
    result = subprocess.run([
        'curl', '-X', 'POST', 'https://dev.to/api/articles',
        '-H', f'api-key: {DEVTO_KEY}',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ], capture_output=True, text=True)
    
    response = json.loads(result.stdout)
    if 'article' in response:
        url = response['article'].get('url', 'https://dev.to/said_olano')
        
        # Save state
        with open('article_state.txt', 'w') as f:
            f.write(f"TITLE:{title}\n")
            f.write(f"URL:{url}\n")
            f.write(f"TAGS:{','.join(tags)}\n")
            f.write(f"TOPIC:{topic}\n")
        
        # Mark topic as used
        with open('temas_post_LinkedIn_usados.txt', 'a') as f:
            f.write(topic + '\n')
        
        print(f"✓ Published: {url}\n")
        print("=== SUCCESS ===")
    else:
        print(f"ERROR: {response}")
        exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
