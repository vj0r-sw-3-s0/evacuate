#!/bin/bash

mkdir /etc/evacuate_engine/
cp settings.ini /etc/evacuate_engine/
touch /var/log/evacuate_engine.log

cp evacuate_engine.py /usr/local/bin/evacuate_engine
cp evacuate_engine.service /etc/systemd/system/
chmod +x /usr/local/bin/evacuate_engine

systemctl daemon-reload
systemctl restart evacuate_engine.service
systemctl status evacuate_engine.service

