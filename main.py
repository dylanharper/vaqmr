"""Google Functions that collect data for DOTUFP, and are triggered by Pub/Sub."""

import vaqmr
import base64
import json

def vaqmr(event, context):
    """Collect recent faves/likes for twitter accounts defined in project config. Triggered by Pub/Sub.

    Args:
         event (dict):  The dictionary with data specific to this type of
         event. The `data` field contains the PubsubMessage message. The
         `attributes` field will contain custom attributes if there are any.
         context (google.cloud.functions.Context): The Cloud Functions event
         metadata. The `event_id` field contains the Pub/Sub message ID. The
         `timestamp` field contains the publish time.

    """
    event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    collector = event_data['collector']
    # work_list = event_data.get('work_list')

    if collector == 'twitter_faves':
        vaqmr.twitter_faves()
    elif collector == 'twitter_timeline':
        vaqmr.twitter_timeline()
    elif collector == 'twitter_home_timeline':
        vaqmr.twitter_home_timeline()
    elif collector == 'web_scrape':
        vaqmr.web_scrape()
    else:
        raise ValueError(f'Unknown collector type: {collector}')
