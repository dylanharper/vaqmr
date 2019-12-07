# Vaqmr

a data collection tool

## Manual (non-scheduled) collection

Web-scrape is able to handle collection requests outside of its config.

```bash
gcloud pubsub topics publish vaqmr --message '{"collector":"web_scrape", "work_list":[{"url":"http://blah.meh","storage_key":"blah"}]}'
```

## Adding a new collector

Add new function in main.py

Add new config in config.yml

Test locally:

```python
import main

main.vaqmr_worker({'collector':'your_new_collector'}, 'context')
```

- check output in gs://dotufp-raw/

- deploy vaqmr

Create a schedule:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Create Job -> Name = twitter-faves -> Target = Pub/Sub -> Topic = vaqmr -> Payload = {"collector":"twitter_faves"}

Test function:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Find the schedule and click Run Now.

- Check [function logs](https://console.cloud.google.com/logs/viewer?project=dotufp&resource=cloud_function%2Ffunction_name%2Fvaqmr_worker%2Fregion%2Fus-central1&minLogLevel=0&expandAll=false).

- Check output file.

## Testing partial worklist

Test locally:

```python
import main

main.vaqmr_worker(event={'collector':'your_new_collector',
                         'work_list':[{'url':'http://blah.meh',
                                       'storage_key':'blah'}]},
                  context='context')
```

Or refer Manual (non-scheduled) collection.

## Monitoring

Errors: <https://console.cloud.google.com/errors?service=vaqmr_worker&time=P7D&order=COUNT_DESC&resolution=OPEN&resolution=ACKNOWLEDGED&project=dotufp&folder&organizationId>

Reference: <https://cloud.google.com/functions/docs/monitoring/>
