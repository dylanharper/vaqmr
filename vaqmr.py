"""Functions used to collect data for DOTUFP projects.

All data collection for DOTUFP is done through these functions.
"""

import json
import yaml
import requests
from requests_oauthlib import OAuth1
from datetime import datetime
from google.cloud import kms_v1
from google.cloud import storage

def _get_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def _get_blob_name(output_prefix, account, timestamp):
    return f'{output_prefix}{account}/{timestamp}.raw'

def _get_config(config_key: str =None):
    """Fetch requested configurations from project config."""
    with open('config.yml', 'r') as config_file:
        project_config = yaml.safe_load(config_file)

    if config_key:
        return project_config[config_key]
    else:
        return project_config

def _get_secrets():
    """Fetch and decrypt project secrets."""
    # get encrypted secrets
    storage_client = storage.Client()
    bucket = storage_client.bucket('dotufp-sm')
    blob = bucket.blob('vaqmr-secrets.v2.json.encrypted')
    ciphertext = blob.download_as_string()

    # decrypt secrets
    kms_client = kms_v1.KeyManagementServiceClient()
    key_name = kms_client.crypto_key_path('secret-manager-258521', 'global', 'dotufp-secrets', 'dotufp-secrets-key')
    secrets = kms_client.decrypt(key_name, ciphertext)

    return json.loads(secrets.plaintext)

def _upload_data(bucket_name: str, blob_name: str, data: str):
    """Upload data to storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(data)


def twitter_faves():
    """Collect recent faves/likes for twitter accounts defined in project config. Triggered by Pub/Sub."""
    config = _get_config('twitter_faves')
    secrets = _get_secrets()

    for account in config['work_list']:
        storage_key = account['key']
        url = 'https://api.twitter.com/1.1/favorites/list.json'
        params = {'count': 100, 'screen_name': storage_key}
        headers = {'Authorization': secrets['twitter']['Bearer']}

        faves = requests.get(url, params=params, headers=headers)
        faves.raise_for_status()

        timestamp = _get_timestamp()
        blob_name = _get_blob_name(config['output_prefix'], storage_key, timestamp)
        _upload_data(config['output_bucket'], blob_name, faves.text)

def twitter_timeline():
    """Collect recent tweets/retweets for twitter accounts defined in project config. Triggered by Pub/Sub."""
    config = _get_config('twitter_timeline')
    secrets = _get_secrets()

    for account in config['work_list']:
        storage_key = account['key']
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {'count': 50, 'screen_name': storage_key, 'include_rts': True}
        headers = {'Authorization': secrets['twitter']['Bearer']}

        faves = requests.get(url, params=params, headers=headers)
        faves.raise_for_status()

        timestamp = _get_timestamp()
        blob_name = _get_blob_name(config['output_prefix'], storage_key, timestamp)
        _upload_data(config['output_bucket'], blob_name, faves.text)

def twitter_home_timeline():
    """Collect recent tweets seen by twitter accounts defined in project config. Triggered by Pub/Sub."""
    config = _get_config('twitter_home_timeline')
    secrets = _get_secrets()

    # looping through work_list doesn't make sense when we only have 1 bearer token
    for account in config['work_list']:
        storage_key = account['key']
        url = 'https://api.twitter.com/1.1/statuses/home_timeline.json'
        client_key = secrets['twitter']['API key']
        client_secret = secrets['twitter']['API secret key']
        resource_owner_key = secrets['twitter']['Access token']
        resource_owner_secret = secrets['twitter']['Access token secret']

        header_oauth = OAuth1(client_key, client_secret,
                                                resource_owner_key, resource_owner_secret,
                                                signature_type='auth_header')

        params = {'count': 100}

        faves = requests.get(url, auth=header_oauth, params=params)
        faves.raise_for_status()

        timestamp = _get_timestamp()
        blob_name = _get_blob_name(config['output_prefix'], storage_key, timestamp)
        _upload_data(config['output_bucket'], blob_name, faves.text)

def web_scrape():
    """Capture public websites defined in project config. Triggered by Pub/Sub."""
    config = _get_config('web_scrape')

    for site in config['work_list']:
        storage_key = site['key']
        url = site['url']
        headers = {'User-Agent': 'Mozilla/5.0'}

        faves = requests.get(url, headers=headers)
        faves.raise_for_status()

        timestamp = _get_timestamp()
        blob_name = _get_blob_name(config['output_prefix'], storage_key, timestamp)
        _upload_data(config['output_bucket'], blob_name, faves.text)
