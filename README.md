# UWC_backend_new
# Setup MySQL
Take scripts in the Scripts folder of the repo and run in MySQL workbench to create a db, according to the following order:
```
Schema.sql
Procedure.sql
Trigger.sql
Insert.sql
```
# Setup OSRM
Download Docker.
Download OpenStreetMap extracts for Vietnam from Geofabrik:
```bash
wget http://download.geofabrik.de/europe/germany/vietnam-latest.osm.pbf
```
## Pre-process the extract with the car profile and start a routing engine HTTP server on port 5000
Store the file within a local directory "${PWD}" self defined.
```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-extract -p /opt/car.lua /data/vietnam-latest.osm.pbf
```
The flag -v "${PWD}:/data" creates the directory /data inside the docker container and makes the current working directory "${PWD}" available there. The file /data/vietnam-latest.osm.pbf inside the container is referring to "${PWD}/vietnam-latest.osm.pbf" on the host. The run may take a wild amount of time and possibly return error. Then:
```bash
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-partition /data/vietnam-latest.osrm
docker run -t -v "${PWD}:/data" osrm/osrm-backend osrm-customize /data/vietnam-latest.osrm
```
Note that vietnam-latest.osrm has a different file extension.
```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/berlin-latest.osrm
```
Make requests against the HTTP server to test:
```bash
curl "http://127.0.0.1:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?steps=true"
```
# setup environment
Clone project from github.  
Config manually the DATABASE_CREDENTIALS section in the uwc_backend/settings.py. Change the password to fit your MySQL account. 
## create virtual environment 
Create new virtualenvironment inside project folder and activate it.
```bash
virtualenv env
.\env\scripts\activate
```
Install all dependencies
```bash
pip install -r requirements.txt
```
Now try to run the local server
```bash
python manage.py runserver 
```
# APIs
## 1. User apis set
all urls in this section begin with http://127.0.0.1:8000/accounts/
### a. authenticate
```
auth/
```
POST: User provides username and password of a backofficer account stored in the db, not the MySQL account, in request body and receives in turn access token.
```
auth/refresh/
```
POST: Refresh token will return new token.
Both of the above requests returns the following response payload:
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
### c. map and route
`
