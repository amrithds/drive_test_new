# create virtual env
python -m venv venv

# os requirements
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
pip install -r requirement.txt

# Install packages using 
pip install <package> && pip freeze > requirements.txt