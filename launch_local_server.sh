#!/bin/bash

# Add --enable_sendmail to enable actual mail sending. Please make sure you update app_dev.yaml with the expected email
# address to send and receive email

/Users/brentpantell/Downloads/google-cloud-sdk/platform/google_appengine/dev_appserver.py app_dev.yaml \
  --datastore_path='~/joobali_local_data_store' \
  --show_mail_body=true