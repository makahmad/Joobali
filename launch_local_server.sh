#!/bin/bash

dev_appserver.py \
  --datastore_path='~/joobali_local_data_store' \
  --show_mail_body=true \
  --logs_path='/tmp/logs/log.txt' \
  ./
