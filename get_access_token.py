import yaml
import requests
from requests_oauthlib import OAuth1Session

# config.ymlから情報を取得
def load_config():
    with open('config.yml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def main():
    config = load_config()
    consumer_key = config['consumer_key']
    consumer_secret = config['consumer_secret']

    # 1. リクエストトークン取得
    request_token_url = 'https://www.hatena.com/oauth/initiate?scope=read_public,write_public,read_private,write_private'
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')
    fetch_response = oauth.fetch_request_token(request_token_url)
    resource_owner_key = fetch_response.get('oauth_token')
    resource_owner_secret = fetch_response.get('oauth_token_secret')
    print('Request Token:', resource_owner_key)
    print('Request Token Secret:', resource_owner_secret)

    # 2. 認証用URLを案内
    base_authorize_url = 'https://www.hatena.ne.jp/oauth/authorize'
    authorization_url = oauth.authorization_url(base_authorize_url)
    print('Go to the following URL and authorize:')
    print(authorization_url)
    verifier = input('Enter the PIN (oauth_verifier) provided by Hatena: ')

    # 3. アクセストークン取得
    access_token_url = 'https://www.hatena.com/oauth/token'
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)
    print('Access Token:', oauth_tokens['oauth_token'])
    print('Access Token Secret:', oauth_tokens['oauth_token_secret'])

if __name__ == '__main__':
    main() 