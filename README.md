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
docker run -t -i -p 5000:5000 -v "${PWD}:/data" osrm/osrm-backend osrm-routed --algorithm mld /data/vietnam-latest.osrm
```
Make requests against the HTTP server to test:
```bash
curl "http://127.0.0.1:5000/route/v1/driving/13.388860,52.517037;13.385983,52.496891?steps=true"
```
# Setup environment
Clone project from github.  
Config manually the DATABASE_CREDENTIALS section in the uwc_backend/settings.py. Change the password to fit your MySQL account. 
```python
DATABASE_CREDENTIALS = {
    'user':'root',
    'password':'${YOUR_PASSWORD}',
    'host':'127.0.0.1',
    'database': 'uwc_2.0'
}
```
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
all urls in this section begin with http://127.0.0.1:8000/
### a. authenticate
```
accounts/auth/
```
POST: User provides **username** and **password** of a backofficer account stored in the db, not the MySQL account, in request body and receives in turn access token.
```
accounts/auth/refresh/
```
POST: Provide **refresh** token and receive new access token.  
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
### ***
```
accounts/employee/
```
GET: Return all employees working under back officer with **request.user['id']**
### ***
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
### ***
```css
map/
```
GET: Return all MCPs managed by the backofficer on map and their details.  
### ***
```
map/route/
```
GET: Return all current routes in the db, excluding their layout (MCPs).  
POST: User provides to request body a list of MCPs, each with these attributes: **MCP_id, longtitude, latitude**. Example payload:
```json
[
    {
        "MCP_id": 7,
        "longtitude": 106.6662570,
        "latitude": 10.7769350
    },
    {
        "MCP_id": 8,
        "longtitude": 106.6634590,
        "latitude": 10.7828160
    }
]
```
Server returns MCPs with orders.  
### ***
```
map/route/id
```
GET: Return the layout of route with **id**.  
PUT: User provides to request body a list of MCPs specified above with the same payload format. Server update layout of the route with **id** and returns MCPs with new orders.  
DELETE: Delete route with **id**.  
### ***
```
map/route/id/optimize
```
GET: Return the optimized layout of a route that trims off MCPs with less thanf 15% load. Orders also are provided.

