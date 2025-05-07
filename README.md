# Hatena Blog Exporter for Obsidian

Export your Hatena Blog articles to Markdown format with frontmatter, optimized for Obsidian Vault integration.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yotofujita/hatena-blog-exporter
cd hatena-blog-exporter
```

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

## Getting Started

### 1. Get Hatena API Credentials

1. Go to [Hatena Developer Center](https://developer.hatena.ne.jp/ja/documents/auth/apis/oauth/consumer/)
2. Log in with your Hatena account
3. Click "OAuth 開発者向け設定ページ" (OAuth Developer Settings)
4. Click "アプリケーションを登録" (Register Application)
5. Fill in the required information:
   - アプリケーション名 (Application Name): Any name you want
   - コールバックURL (Callback URL): `http://localhost:8000/callback`
   - スコープ (Scope): Select `read_private` and `write_private`
6. After registration, you'll get:
   - Consumer Key
   - Consumer Secret

### 2. Get User ID and Blog ID

Your User ID and Blog ID are embeded in your blog URL: `https://blog.hatena.ne.jp/<User ID>/<Blog ID>/`

### 3. Get Access Token and Access Token Secret

### Configuration

1. Add credential information to config.yml:

```yaml
consumer_key: <Consumer Key>
consumer_secret: <Consumer Secret>
access_token: 
access_token_secret: 
user_id: <User ID>
blog_id: <Blog ID>
```

2. Run the access token generator:

```bash
python get_access_token.py
```

4. Follow the prompts to:
   - Open the authorization URL in your browser
   - Log in to Hatena
   - Authorize the application
   - Enter the verification code
5. The script will output Access Token and Access Token Secret

## Usage

1. Add credential information to config.yml:

```yaml
consumer_key: <Consumer Key>
consumer_secret: <Consumer Secret>
access_token: <Access Token>
access_token_secret: <Access Token Secret>
user_id: <User ID>
blog_id: <Blog ID>
```

2. Run the export script:
```bash
python export_hatena_to_md.py
```

The script will:
- Export all blog posts as Markdown files with frontmatter
- Download and save images locally
- Replace image URLs in the content with local paths
- Save files in a flat structure under the `HatenaBlog` directory

## Output Format

Each exported Markdown file includes:
- Frontmatter with metadata (title, date, categories, tags, draft status)
- Content in Markdown format
- Local image references

Example frontmatter:
```yaml
---
title: "Your Blog Post Title"
date: "2024-03-21T12:00:00+09:00"
categories: ["Category1", "Category2"]
tags: ["tag1", "tag2"]
draft: false
---
```

## Features

- OAuth authentication with Hatena API
- Pagination support for retrieving all posts
- Image download and local path replacement
- Frontmatter generation with metadata
- Flat file structure for optimal Obsidian/Cursor integration

## Notes

- The script creates a `HatenaBlog` directory for exported files
- Images are stored in an `images` subdirectory
- All posts are saved with frontmatter for better searchability in Obsidian/Cursor

## License

[MIT License](http://opensource.org/licenses/MIT)
