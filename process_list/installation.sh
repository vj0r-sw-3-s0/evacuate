#!/bin/bash

mkdir /etc/process_list/
cp settings.ini /etc/process_list/
touch /var/log/process_list.log

cp process_list.py /usr/local/bin/process_list
cp process_list.service /etc/systemd/system/
chmod +x /usr/local/bin/process_list

systemctl daemon-reload
systemctl restart process_list.service
systemctl status process_list.service

