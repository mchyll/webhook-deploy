cd /home/http/API && \
systemctl stop tihlde-web-api && \
git checkout production && \
git pull && \
systemctl start tihlde-web-api
