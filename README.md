# Vaqmr

## Deploy a collector

```bash
gcloud functions deploy twitter_faves --runtime python37 --trigger-topic twitter-faves
```

## Adding a new collector

Add new function in main.py

Add new config in config.yml

Create a new Pub/Sub:

```bash
gcloud pubsub topics create twitter-faves
gcloud pubsub subscriptions create twitter-faves-sub --topic twitter-faves
```

Create a schedule:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Create Job -> Name = twitter-faves -> Target = Pub/Sub -> Topic = twitter-faves

Deploy collector

Test function:

- <https://console.cloud.google.com/cloudscheduler?project=dotufp>

- Find the schedule and click Run Now.

- Check function logs.

- Check output file.

## Monitoring

Errors: <https://console.cloud.google.com/errors?time=P7D&order=COUNT_DESC&resolution=OPEN&resolution=ACKNOWLEDGED&project=dotufp&folder&organizationId>

### Monitoring References

<https://cloud.google.com/functions/docs/monitoring/>
