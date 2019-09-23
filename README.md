# webhook-deploy
Continuous deployment with GitHub Webhooks

## Setup
1. Clone this repository into `/usr/local/bin/webhook-deploy`
2. Generate a secret token with `python -c 'import secrets; print(secrets.token_hex(32))'` and paste it in a file named `secret.txt`
3. Create the directory `/var/log/webhook-deployments` for storing logs
4. Put your deployment scripts in the directory `deployment-scripts`
5. Configure your deployments in `config.yml`
6. Enable and start the systemd service:
   ```
   cp webhook-deploy.service /etc/systemd/system/
   systemctl daemon-reload
   systemctl enable webhook-deploy.service
   systemctl start webhook-deploy.service
   ```
