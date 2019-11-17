"""Google Functions that collect data for DOTUFP, and are triggered by Pub/Sub."""

import vaqmr
import requests
from requests_oauthlib import OAuth1
from datetime import datetime

def twitter_faves(event, context):
    """Collect recent faves/likes for twitter accounts defined in project config. Triggered by Pub/Sub.

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.

    """
    config = vaqmr.get_config('twitter_faves')
    secrets = vaqmr.get_secrets()

    for account in config['work_list']:
        url = 'https://api.twitter.com/1.1/favorites/list.json'
        params = {'count': 100, 'screen_name': account}
        headers = {'Authorization': secrets['twitter_bearer']}

        faves = requests.get(url, params=params, headers=headers)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        blob_name = f'{config["output_prefix"]}{account}/{timestamp}.raw'

        vaqmr.upload_data(config['output_bucket'], blob_name, faves.text)

def twitter_timeline(event, context):
    """Collect recent tweets/retweets for twitter accounts defined in project config. Triggered by Pub/Sub.

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.

    """
    config = vaqmr.get_config('twitter_timeline')
    secrets = vaqmr.get_secrets()

    for account in config['work_list']:
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {'count': 50, 'screen_name': account, 'include_rts': True}
        headers = {'Authorization': secrets['twitter_bearer']}

        faves = requests.get(url, params=params, headers=headers)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        blob_name = f'{config["output_prefix"]}{account}/{timestamp}.raw'

        vaqmr.upload_data(config['output_bucket'], blob_name, faves.text)

def twitter_home_timeline(event, context):
    """Collect recent tweets seen by twitter accounts defined in project config. Triggered by Pub/Sub.

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.

    """
    config = vaqmr.get_config('twitter_home_timeline')
    secrets = vaqmr.get_secrets()

    # looping through work_list doesn't make sense when we only have 1 bearer token
    for account in config['work_list']:
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
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        blob_name = f'{config["output_prefix"]}{account}/{timestamp}.raw'

        vaqmr.upload_data(config['output_bucket'], blob_name, faves.text)
