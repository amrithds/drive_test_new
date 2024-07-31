sudo cp server/apache/* /etc/apache2/sites-available/
sudo systemctl reload apache2
#activate sites
sudo a2ensite drivetest.conf
sudo a2ensite frontend.conf