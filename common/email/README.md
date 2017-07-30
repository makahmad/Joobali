# How to setup your local mailling enviornment (MAC)

The following instruction will help you setup your local `sendmail`
command line to work properly with local app-engine server

#### Setup Sendmail command with your @joobali.com email
1) Create a local file to store our credentials:
    ```bash
    sudo vim /etc/postfix/sasl_passwd
    ```

2) Add a line like the following, remember to change it to your @joobali.com email address

    ```bash
    smtp.gmail.com:587 username@joobali.com:joobali_password
    ```
3) Then run:

    ```bash
    sudo postmap /etc/postfix/sasl_passwd
    ```

4) Prepare the postfix main config file:

    ```bash
    sudo vim /etc/postfix/main.cf
    ```

5) Add/update these lines

    ```
    relayhost=smtp.gmail.com:587
    smtp_sasl_auth_enable=yes
    smtp_sasl_password_maps=hash:/etc/postfix/sasl_passwd
    smtp_use_tls=yes
    smtp_tls_security_level=encrypt
    tls_random_source=dev:/dev/urandom
    smtp_sasl_security_options = noanonymous
    smtp_always_send_ehlo = yes
    smtp_sasl_mechanism_filter = plain
    ```
    
6) Stop the mailling service

    ```bash
    sudo postfix stop
    ```

7) Start the mailling service
    ```bash
    sudo postfix start
    ```

8) Check the queue for any errors
    ```bash
    mailq
    ```

### Update the Your local server to run with sendmail

1) Update the `launch_local_server.sh` file, your new file should looks like
    ```bash
    #!/bin/bash
    
    dev_appserver.py app_dev.yaml \
      --datastore_path='~/joobali_local_data_store' \
      --enable_sendmail
    ```
2) Update the app_dev.yaml file with the overriding email in `OVERRIDING_EMAIL` enviornmental variable

### Special Notes:
It is possible that your first email will not be sent successfully, because google mail by default disable
connection from you terminal. 

You will get a warning mail with subject **Review blocked sign-in attempt**.
Just follow the instruction to enable the 'un-safe access', and your next mail should be able to go through?

You may need to run `sudo postfix start` again after you restart your computer, but there should be no other configuration