#!/bin/bash

#ssh -i ~/.ssh/id_rsa 18.205.194.28 <<EOF
ssh -i ~/.ssh/id_rsa 18.205.194.28
echo 'logged in'
sudo -i
echo 'superuser'
cd /var/www/html/Gyasi_Ecommerce
# git pull origin main
# . venv/bin/activate
# pip install -r requirements.txt
# python3 manage.py makemigrations
# python3 manage.py migrate  --run-syncdb
# sudo systemctl restart apache2
exit
#EOF