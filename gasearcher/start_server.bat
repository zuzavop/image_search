py -m pip install --upgrade pip

py -m pip install --user virtualenv

py -m venv env

call .\env\Scripts\activate.bat

py -m pip install -r requirements.txt

python manage.py migrate

python manage.py compilemessages

python manage.py runserver