# UWC_backend_new
# Setup MySQL
Take scripts in the "MySQL Scripts" folder of the repo and run in MySQL workbench/MySQL Shell to create a db, according to the following order:
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
wget https://download.geofabrik.de/asia/vietnam-latest.osm.pbf
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
```css
accounts/auth/
```
POST: User provides **username** and **password** of a backofficer account stored in the db, not the MySQL account, in request body and receives in turn access token.
```css
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
```css
accounts/employee/
```
GET: Return all employees working under back officer with **request.user['id']**.  
POSt: User includes these fields in request body: **username, password, name, address, gender, phone, email, role, salary, birth,**. Example payload:
```json
{
    "username": "____",
    "password": "____",
    "name": "____",
    "address": "____",
    "gender": "male/female",
    "phone": "____",
    "email": "____",
    "role": 1,
    "salary": 6000000,
    "birth": "YYYY-MM-DD",
}
```
### ***
```css
accounts/employee/id/
```
GET: Return an employee detail  
PUT: User updates an employee by including these fields in request body: **name, address, birth, gender, phone, email, manager_id, vehicle_id, start_date, radius, mcp_id, route_id, is_working, role, salary,**. Example payload:
```json
{
    "name": "____",
    "address": "____",
    "birth": "YYYY-MM-DD",
    "gender": "male/female",
    "phone": "____",
    "email": "____",
    "manager_id": null,
    "vehicle_id": 23,
    "startdate": "YYYY-MM-DD",
    "radius": 324,
    "mcp_id": 3,
    "route_id": null,
    "is_working": null,
    "role": 1,
    "salary": 6000000
}
```
DELETE: Delete an employee data with **id**.
```css
accounts/employee/id/schedule
```
POST: User creates a workshift for employee with **id** by including these fields in request body: **start_time, end_time, weekday**. Example payload:
```json
{
    "start_time": 12,
    "end_time": 18,
    "weekday": "Mon/Tue/Wed/Thur/Fri/Sat/Sun"
}
```
### ***
```css
accounts/employee/emp_id/schedule/shift_id
```
GET: Return a workshift with **shift_id** of employee **emp_id**.  
DELETE: Delete a workshift with **shift_id** of employee **emp_id**.  
### c. map and route
### ***
```css
map/
```
GET: Return all MCPs managed by the backofficer on map and their details.  
### ***
```css
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
```css
map/route/id
```
GET: Return the layout of route with **id**.  
PUT: User provides to request body a list of MCPs specified above with the same payload format. Server update layout of the route with **id** and returns MCPs with new orders.  
DELETE: Delete route with **id**.  
### ***
```css
map/route/id/optimize
```
GET: Return the optimized layout of a route that trims off MCPs with less thanf 15% load. Orders also are provided.

