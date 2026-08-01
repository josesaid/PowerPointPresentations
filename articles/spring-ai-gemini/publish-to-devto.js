#!/usr/bin/env node

const https = require('https');
const fs = require('fs');
const path = require('path');

// Configuración
const API_KEY = process.env.DEVTO_API_KEY || '6RANyTeipK9AgyWN7Q2T1PLH';
const ARTICLE_FILE = process.argv[2] || 'article_EN.md';

console.log('📝 Dev.to Publisher v1');
console.log('━━━━━━━━━━━━━━━━━━━━━');

// Leer artículo
if (!fs.existsSync(ARTICLE_FILE)) {
  console.error('❌ Article file not found:', ARTICLE_FILE);
  process.exit(1);
}

const articleContent = fs.readFileSync(ARTICLE_FILE, 'utf8');
const titleMatch = articleContent.match(/^# (.+)$/m);
const title = titleMatch ? titleMatch[1].trim() : 'Article';
const bodyMarkdown = articleContent.split('\n').slice(2).join('\n');

console.log('📄 Article:', title);
console.log('📏 Size:', bodyMarkdown.length, 'chars');

// Payload
const payload = JSON.stringify({
  article: {
    title: title,
    body_markdown: bodyMarkdown,
    published: true,
    tags: ['springai', 'java', 'gemini', 'ai'],
    canonical_url: ''
  }
});

// Opciones HTTPS
const options = {
  hostname: 'dev.to',
  port: 443,
  path: '/api/articles',
  method: 'POST',
  headers: {
    'api-key': API_KEY,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload),
    'User-Agent': 'GitHub-Actions-Claude'
  },
  timeout: 30000
};

console.log('🔄 Publishing to dev.to...');

// Request
const req = https.request(options, (res) => {
  let data = '';

  res.on('data', (chunk) => {
    data += chunk;
  });

  res.on('end', () => {
    console.log('📊 Status:', res.statusCode);

    if (res.statusCode >= 200 && res.statusCode < 300) {
      try {
        const response = JSON.parse(data);
        if (response.article && response.article.url) {
          console.log('✅ Published successfully!');
          console.log('📎 URL:', response.article.url);
          console.log('🔗 Slug:', response.article.slug);

          // Guardar estado
          const state = {
            title: response.article.title,
            url: response.article.url,
            slug: response.article.slug,
            id: response.article.id,
            tags: ['springai', 'java', 'gemini', 'ai'],
            published_at: new Date().toISOString(),
            status: 'published'
          };

          fs.writeFileSync('devto-published-state.json', JSON.stringify(state, null, 2));
          console.log('💾 State saved to devto-published-state.json');

          // Output para GitHub Actions
          console.log(`::set-output name=devto_url::${response.article.url}`);
          console.log(`::set-output name=devto_slug::${response.article.slug}`);

          process.exit(0);
        } else {
          console.error('❌ No article in response:', data);
          process.exit(1);
        }
      } catch (e) {
        console.error('❌ Parse error:', e.message);
        console.error('Response:', data);
        process.exit(1);
      }
    } else {
      console.error('❌ API Error:', res.statusCode);
      console.error('Response:', data);

      // Detectar errores comunes
      if (data.includes('exist')) {
        console.log('⚠️  Article might already exist');
      }
      if (data.includes('authenticate') || data.includes('401')) {
        console.log('⚠️  Authentication failed - check API key');
      }

      process.exit(1);
    }
  });
});

req.on('error', (error) => {
  console.error('❌ Request error:', error.message);
  process.exit(1);
});

req.on('timeout', () => {
  console.error('❌ Timeout');
  req.destroy();
  process.exit(1);
});

req.write(payload);
req.end();
