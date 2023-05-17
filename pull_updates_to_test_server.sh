#!/bin/bash

#ssh -i ~/.ssh/id_rsa 18.205.194.28 <<EOF
# ssh ubuntu@172.31.82.198
# echo 'logged in'
# sudo -i
# echo 'superuser'
# cp -R /var/www/html/Gyasi_Ecommerce/workspace/DjangoApp/* /var/www/html/Gyasi_Ecommerce/
# cd /var/www/html/Gyasi_Ecommerce
# git pull origin main
if [ -d '/var/www/jenkins-slave/workspace/DjangoApp/venv/' ]
then
    echo "skipping creating virtual env"
else
    virtualenv venv
fi
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate  --run-syncdb
deactivate
sudo systemctl restart apache2
#EOF
