#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
from datetime import datetime

print("=== START ===\n")

print("1. Checking API keys...")
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DEVTO_KEY = os.environ.get('DEVTO_API_KEY', '')

if not ANTHROPIC_KEY or not DEVTO_KEY:
    print("ERROR: Missing API keys")
    exit(1)

print(f"✓ ANTHROPIC_API_KEY: {len(ANTHROPIC_KEY)} chars, starts with: {ANTHROPIC_KEY[:10]}")
print(f"✓ DEVTO_API_KEY: {len(DEVTO_KEY)} chars, starts with: {DEVTO_KEY[:10]}")
print(f"  Expected: sRAZfCZ2EZ")
print(f"  Match: {DEVTO_KEY.startswith('sRAZfCZ2EZ')}\n")



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
            'max_tokens': 2000,
            'messages': [{
                'role': 'user',
                'content': '''Write a technical blog post about Java and Spring Boot.

Output format - use exactly this format with these delimiters:
TITLE: Your Blog Title Here
TAGS: tag1,tag2,tag3,tag4
BODY:
Your markdown content here. Include headers, paragraphs, code blocks.
Use proper markdown syntax.
END_BODY

Do not include anything else, just follow this exact format.'''
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
        
        lines = text.split('\n')
        title = ""
        tags = []
        body = ""
        
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
        
        title = title or 'Untitled'
        tags = tags or ['java', 'programming']
        body = body.strip() or f'# {title}\n\nAuto-generated article'
        
        # Add timestamp to title to make it unique
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        unique_title = f"{title} ({timestamp})"
        
        print(f"✓ Title: {unique_title[:60]}")
        print(f"✓ Tags: {tags}")
        print(f"✓ Body length: {len(body)} chars\n")
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)

print("3. Publishing to dev.to...")
try:
    req = urllib.request.Request(
        'https://dev.to/api/articles',
        data=json.dumps({
            'article': {
                'title': unique_title,
                'body_markdown': body,
                'published': False,
                'tags': tags[:4]
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
    print(f"✗ HTTP {e.code}")
    try:
        body_err = e.read().decode() if e.fp else 'No response body'
        print(f"Response: {body_err}")
    except:
        print("Could not read error response")
    exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    exit(1)
