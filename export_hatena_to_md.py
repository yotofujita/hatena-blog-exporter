import yaml
import requests
import os
import re
from xml.etree import ElementTree as ET
from requests_oauthlib import OAuth1
from urllib.parse import urlparse

# 設定ファイルの読み込み
def load_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)

def download_media(url, out_dir, auth=None):
    if not url:
        return None
    os.makedirs(out_dir, exist_ok=True)
    filename = os.path.basename(urlparse(url).path)
    filepath = os.path.join(out_dir, filename)
    try:
        resp = requests.get(url, auth=auth)
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            return filepath
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None

def extract_metadata(entry, ns):
    # タイトル・本文
    title = entry.find('atom:title', ns).text
    content = entry.find('atom:content', ns).text or ''
    published = entry.find('atom:published', ns).text[:10]
    # カテゴリ
    categories = [c.attrib['term'] for c in entry.findall('atom:category', ns)]
    # タグ（はてなブログではカテゴリがタグも兼ねる場合あり）
    tags = categories.copy()
    # 下書き判定
    draft_elem = entry.find('{http://purl.org/atom-blog/ns#}draft')
    draft = draft_elem.text.lower() == 'yes' if draft_elem is not None else False
    # 画像・添付ファイルURL抽出（imgタグのsrc属性）
    img_urls = re.findall(r'<img[^>]+src=["\"]([^"\"]+)["\"]', content)
    # enclosure（添付ファイル）
    enclosure_links = [l.attrib['href'] for l in entry.findall("atom:link[@rel='enclosure']", ns)]
    return {
        'title': title,
        'content': content,
        'published': published,
        'categories': categories,
        'tags': tags,
        'draft': draft,
        'img_urls': img_urls,
        'enclosure_links': enclosure_links
    }

def save_entries(entries, out_base_dir, auth=None):
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    os.makedirs(out_base_dir, exist_ok=True)
    media_dir = os.path.join(out_base_dir, 'media')
    for entry in entries:
        meta = extract_metadata(entry, ns)
        # 画像・添付ファイルのダウンロード
        local_img_paths = []
        for url in meta['img_urls']:
            local_path = download_media(url, media_dir, auth=auth)
            if local_path:
                local_img_paths.append(local_path)
        for url in meta['enclosure_links']:
            download_media(url, media_dir, auth=auth)
        # 本文中の画像URLをローカルパスに置換
        content = meta['content']
        for url, local_path in zip(meta['img_urls'], local_img_paths):
            content = content.replace(url, os.path.relpath(local_path, out_base_dir))
        # frontmatter生成
        frontmatter = '---\n'
        frontmatter += f'title: "{meta["title"]}"\n'
        frontmatter += f'date: {meta["published"]}\n'
        frontmatter += f'categories: {meta["categories"]}\n'
        frontmatter += f'tags: {meta["tags"]}\n'
        frontmatter += f'draft: {meta["draft"]}\n'
        frontmatter += '---\n\n'
        filename = f"{meta['published']}_{sanitize_filename(meta['title'])}.md"
        filepath = os.path.join(out_base_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(frontmatter)
            f.write(content + '\n')
        print(f"Saved: {filepath}")

def fetch_entries(config):
    blog_id = config['blog_id']
    user_id = config['user_id']
    url = f'https://blog.hatena.ne.jp/{user_id}/{blog_id}/atom/entry'
    auth = OAuth1(
        config['consumer_key'],
        config['consumer_secret'],
        config['access_token'],
        config['access_token_secret']
    )
    headers = {'Accept': 'application/x.atom+xml'}
    entries = []
    while url:
        resp = requests.get(url, headers=headers, auth=auth)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code}")
            print(resp.text)
            break
        root = ET.fromstring(resp.content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entry_list = root.findall('atom:entry', ns)
        entries.extend(entry_list)
        print(f"Fetched {len(entry_list)} entries (total: {len(entries)})")
        # nextリンクを探す
        next_link = root.find("atom:link[@rel='next']", ns)
        if next_link is not None:
            url = next_link.attrib['href']
        else:
            url = None
    return entries, auth

def main():
    config = load_config()
    # Obsidian VaultのHatenaBlogフォルダに直接書き出し
    out_dir = '/mnt/g/マイドライブ/Obsidian/Main/HatenaBlog'  # 必要に応じてパスを調整
    entries, auth = fetch_entries(config)
    save_entries(entries, out_dir, auth=auth)

if __name__ == '__main__':
    main() 