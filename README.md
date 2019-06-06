# webhook-deploy
Continuous deployment with GitHub Webhooks

## Setup
Generate a secret token with `python -c 'import secrets; print(secrets.token_hex(32))'` and paste it in a file named `secret.txt`.