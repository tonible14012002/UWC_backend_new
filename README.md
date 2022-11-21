# UWC_backend_new
# setup environment
Clone project from github
### create virtual environment 
Create new virtualenvironment inside project folder and activate it.
```bash
virtualenv env
.\env\scripts\activate
```
Install all dependencies
```bash
pip install -r requirements.txt
```
Create new mysql db, and connect it to our django pj. 
Config manually the DATABASE_CREDENTIALS section in the uwc_backend/settings.py. Change the password to fit your account
Make sure the db is connected correctly. 
Run scripts in the Scripts folder in MySQL workbench to create a db, according to the following order
```
Schema.sql
Procedure.sql
Trigger.sql
Insert.sql
```
```bash
python manage.py makemigrations
python manage.py migrate
```
Now try to run the local server
```bash
python manage.py runserver 
```
Create a superuser account.
```bash
python manage.py createsuperuser
```
Now you can login into django built-in admin page at http://127.0.0.1:8000/admin/.
You can also modify the admin page by config in the (app_name)/admin.py.
# APIs
## 1. User apis set
all urls in this section begin with http://127.0.0.1:8000/accounts/
### a. authenticate
Provide username and password in request body.
refresh token will return new token.
```
auth/token/
auth/refresh/
```
Response payload
```json
{
    "refresh": "jwt_refresh",
    "access": "jwt_access",
    "user": {
        "user_fields": "values"
    }
}
```
### b. user apis set
urls will be in this format 
```bash
http://127.0.0.1:8000/accounts/back-officers/{id}/
http://127.0.0.1:8000/accounts/employees/{id}/
```
- provide user_id if you want to update, retrieve, delete specific user (PUT, GET, DELETE).
##### register
Request payload for register (POST) must include these fields: **username, password, last_name , first_name, confirm_password, address, phone, birth,**
- If you are creating an employee user, provide additional employee field: **manager_id, role**
- Example payload
```json
{
    "username": "____",
    "password": "____",
    "confirm_password": "____",
    "email": "____",
    "phone": "____",
    "address": "____",
    "birth": "YYYY-MM-DD",
    "manager_id": "back_officer id, not user_id",
    "role": "JANITOR/COLLECTOR"
}
```
However if your wanna update an employee user, you can provide a nested json employee field. In updating, no fields is required, you can update many fields or just one. Payload example:
```json
{
    "user_fiels...": "update value",
    "employee": {
        "role": "COLLECTOR/JANITOR",
        "start_date": "MMMM-YY-DD",
        "is_working": "true/false",
        "manager": "new manager id"
    }
}
```
