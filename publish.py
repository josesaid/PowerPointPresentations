#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error

print("=== START ===\n")

print("1. Checking API keys...")
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DEVTO_KEY = os.environ.get('DEVTO_API_KEY', '')

if not ANTHROPIC_KEY or not DEVTO_KEY:
    print("ERROR: Missing API keys")
    exit(1)
print(f"✓ ANTHROPIC_API_KEY: {len(ANTHROPIC_KEY)} chars")
print(f"✓ DEVTO_API_KEY: {len(DEVTO_KEY)} chars\n")

print("2. Generating article with Claude...")
try:
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps({
            'model': 'claude-opus-4-8',
            'max_tokens': 1500,
            'messages': [{
                'role': 'user',
                'content': 'Write a technical blog post about Java. Respond with ONLY a JSON object with these exact fields: title (string), body_markdown (string), tags (array). No other text. Just raw JSON.'
            }]
        }).encode(),
        headers={
            'x-api-key': ANTHROPIC_KEY,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as res:
        if res.status != 200:
            print(f"ERROR: Claude {res.status}")
            exit(1)
        data = json.loads(res.read())
        text = data['content'][0]['text'].strip()
        
        s = text.find('{')
        e = text.rfind('}') + 1
        if s == -1 or e == 0:
            print(f"ERROR: No JSON found")
            exit(1)
        
        json_str = text[s:e]
        try:
            article = json.loads(json_str)
        except json.JSONDecodeError as je:
            print(f"ERROR parsing JSON: {je}")
            exit(1)
        
        title = article.get('title', 'Untitled')
        print(f"✓ Title: {title[:60]}\n")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

print("3. Testing dev.to API key...")
try:
    req = urllib.request.Request(
        'https://dev.to/api/me',
        headers={'api-key': DEVTO_KEY}
    )
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read())
        username = data.get('username', 'Unknown')
        print(f"✓ API Key valid! User: {username}\n")
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ''
    print(f"✗ API Key test FAILED: HTTP {e.code}")
    print(f"Response: {body}")
    print(f"\nThe API key may be invalid, revoked, or belong to a different account.")
    exit(1)

print("4. Publishing to dev.to...")
try:
    body = article.get('body_markdown', f'# {title}\n\nAuto-generated article')
    tags = article.get('tags', ['java'])
    if not isinstance(tags, list):
        tags = ['java']
    tags = tags[:4]
    
    req = urllib.request.Request(
        'https://dev.to/api/articles',
        data=json.dumps({
            'article': {
                'title': title,
                'body_markdown': body,
                'published': True,
                'tags': tags
            }
        }).encode(),
        headers={
            'api-key': DEVTO_KEY,
            'content-type': 'application/json'
        }
    )
    with urllib.request.urlopen(req) as res:
        if res.status in [200, 201]:
            data = json.loads(res.read())
            url = data.get('article', {}).get('url', 'https://dev.to/said_olano')
            print(f"✓ Published: {url}\n")
            print("=== SUCCESS ===")
        else:
            print(f"ERROR: dev.to {res.status}")
            exit(1)
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else '{}'
    print(f"✗ HTTP {e.code}")
    print(f"Error: {body}")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
