To run automatically:
Run `sudo crontab -e`
Add `@reboot sleep 10; sh /home/pi/projects/cryptopi/launcher.sh >/home/pi/logs/cronlog 2>&1`
