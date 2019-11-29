# Vaqmr

## Adding a new collector

Add new function in main.py

Add new config in config.yml

Create a schedule:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Create Job -> Name = twitter-faves -> Target = Pub/Sub -> Topic = vaqmr -> Payload = {"collector":"twitter_faves"}

Test function:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Find the schedule and click Run Now.

- Check [function logs](https://console.cloud.google.com/logs/viewer?project=dotufp&resource=cloud_function%2Ffunction_name%2Fvaqmr_worker%2Fregion%2Fus-central1&minLogLevel=0&expandAll=false).

- Check output file.

## Monitoring

Errors: <https://console.cloud.google.com/errors?service=vaqmr_worker&time=P7D&order=COUNT_DESC&resolution=OPEN&resolution=ACKNOWLEDGED&project=dotufp&folder&organizationId>

Reference: <https://cloud.google.com/functions/docs/monitoring/>
