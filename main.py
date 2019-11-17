"""Google Functions that collect data for DOTUFP, and are triggered by Pub/Sub."""

import vaqmr
import requests
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
        params = {'count': 200, 'screen_name': account}
        headers = {'Authorization': secrets['twitter_bearer']}

        faves = requests.get(url, params=params, headers=headers)
        timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        blob_name = f'{config["output_prefix"]}{account}/{timestamp}.raw'

        vaqmr.upload_data(config['output_bucket'], blob_name, faves.text)
