https://myneighborville.me

Aplikację opracowali: Jakub Ołdziejewski, Krzysztof Wiśniewski, Rafał Popiel ze szkoły Elektroniczne Zakłady Naukowe.

Użyte usługi i technologie:<br>
Python - Django<br>
JavaScript - Vanilla, Ajax, JQuery<br>
Linode - Ubuntu Server 18.04<br>
Namecheap - myneighborville.me , SSL<br>
Google - Maps Platform API<br>

Lokalna instalacja Windows 
1. Zainstaluj git i sklonuj repozytorium
[link do gita]
git clone https://github.com/jakuboldziej/hack-heroes.git
2. Zainstaluj python python.org
3. Stwórz wirtualne środowisko python w folderze /hack-heroes i zainstaluj wymagania.
python -m venv venv
 pip install -r requirements.txt
4. Za pomocą wiersza poleceń, w folderze /hack-heroes utwórz bazę danych i dodaj administratora oraz odpal lokalny serwer
python manage.py migrate --run-syncdb
python manage.py createsuperuser
python manage.py runserver
6. Zaloguj się do Panelu Administracyjnego Django za pomocą wcześniej podanych danych. Utwórz obiekt WebsiteUser z relacją do twojego użytkownika oraz nadaną dowolną lokalizacją.
7. Jeżeli chcesz aby twoje konto miało dostęp do korzystania z mapy, musisz zarejestrować w /register nowego użytkownika z taką samą lokalizacją jak twoje konto.
