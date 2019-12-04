"""Google Functions that collect data for DOTUFP, and are triggered by Pub/Sub."""

import vaqmr
import base64
import json

def vaqmr_worker(event, context):
    """Collect recent faves/likes for twitter accounts defined in project config. Triggered by Pub/Sub.

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.
    Returns:
        None; the output is written to Storage.

    """
    event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    collector = event_data['collector']
    print(f'Collector: {collector}')
    # work_list = event_data.get('work_list')

    if collector == 'twitter_faves':
        vaqmr.twitter_faves(event_data)
    elif collector == 'twitter_timeline':
        vaqmr.twitter_timeline(event_data)
    elif collector == 'twitter_home_timeline':
        vaqmr.twitter_home_timeline(event_data)
    elif collector == 'web_scrape':
        vaqmr.web_scrape(event_data)
    else:
        raise ValueError(f'Unknown collector type: {collector}')
