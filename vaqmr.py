"""Functions used to collect data for DOTUFP projects.

All data collection for DOTUFP is done through these functions.
"""

import json
import yaml
from google.cloud import kms_v1
from google.cloud import storage

def get_config(config_key: str =None):
    """Fetch requested configurations from project config."""
    with open('config.yml', 'r') as config_file:
        project_config = yaml.safe_load(config_file)

    if config_key:
        return project_config[config_key]
    else:
        return project_config


def get_secrets():
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


def upload_data(bucket_name: str, blob_name: str, data: str):
    """Upload data to storage."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    blob.upload_from_string(data)
