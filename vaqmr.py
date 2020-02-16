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
from typing import Dict, Union


def _get_timestamp():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def _get_blob_name(output_prefix, account, timestamp):
    return f'{output_prefix}/{account}/{timestamp}.raw'


def _get_config(config_key: str = None):
    """Fetch requested configurations from project config."""
    with open('config.yml', 'r') as config_file:
        project_config = yaml.safe_load(config_file)

    if config_key:
        return project_config[config_key]

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


def twitter_faves(event_data: dict):
    """Collect recent faves/likes for twitter accounts defined in project config."""
    secrets = _get_secrets()
    config = _get_config('twitter_faves')
    work_list = event_data.get('work_list') or config['work_list']

    for work_item in work_list:
        params = {'count': 100, 'screen_name': work_item['storage_key'], 'tweet_mode': 'extended'}
        headers = {'Authorization': secrets['twitter']['Bearer']}

        response = requests.get(config['url'], params=params, headers=headers)
        response.raise_for_status()

        blob_name = _get_blob_name(config['output_prefix'], work_item['storage_key'], _get_timestamp())
        _upload_data(config['output_bucket'], blob_name, response.text)


def twitter_timeline(event_data: dict):
    """Collect recent tweets/retweets for twitter accounts defined in project config."""
    secrets = _get_secrets()
    config = _get_config('twitter_timeline')
    work_list = event_data.get('work_list') or config['work_list']

    for work_item in work_list:
        params = {'count': 50, 'user_id': work_item['twitter_id'], 'include_rts': True, 'tweet_mode': 'extended'}
        headers = {'Authorization': secrets['twitter']['Bearer']}

        response = requests.get(config['url'], params=params, headers=headers)
        response.raise_for_status()

        blob_name = _get_blob_name(config['output_prefix'], work_item['storage_key'], _get_timestamp())
        _upload_data(config['output_bucket'], blob_name, response.text)


def twitter_home_timeline(event_data: dict):
    """Collect recent tweets seen by twitter accounts defined in project config."""
    secrets = _get_secrets()
    config = _get_config('twitter_home_timeline')
    work_list = event_data.get('work_list') or config['work_list']

    # looping through work_list doesn't make sense when we only have 1 bearer token
    for work_item in work_list:
        header_oauth = OAuth1(secrets['twitter']['API key'],
                              secrets['twitter']['API secret key'],
                              secrets['twitter']['Access token'],
                              secrets['twitter']['Access token secret'],
                              signature_type='auth_header')

        params: Dict[str, Union[int, str]] = {'count': 100, 'tweet_mode': 'extended'}

        response = requests.get(config['url'], auth=header_oauth, params=params)
        response.raise_for_status()

        blob_name = _get_blob_name(config['output_prefix'], work_item['storage_key'], _get_timestamp())
        _upload_data(config['output_bucket'], blob_name, response.text)


def web_scrape(event_data: dict):
    """Capture public websites defined in project config."""
    config = _get_config('web_scrape')
    work_list = event_data.get('work_list') or config['work_list']

    for work_item in work_list:
        url = work_item['url']
        headers = {'User-Agent': 'Mozilla/5.0'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        blob_name = _get_blob_name(config['output_prefix'], work_item['storage_key'], _get_timestamp())
        _upload_data(config['output_bucket'], blob_name, response.text)
