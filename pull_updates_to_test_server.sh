#!/bin/bash

ssh ubuntu@3.95.224.17 <<EOF
  sudo -i
  cd /var/www/html/Gyasi_Ecommerce
  git pull origin main
  pip install -r requirements.txt
  python3 manage.py makemigrations
  python3 manage.py migrate  --run-syncdb
  sudo systemctl reload apache2.service
  exit
EOF