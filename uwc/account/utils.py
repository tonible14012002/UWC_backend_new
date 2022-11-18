from mysql import connector as mysql_connector
from django.conf import settings

def connect_db():
    return mysql_connector.connect(**settings.DATABASE_CREDENTIALS)

def user_db_convertor(user_db_values):
    user_fields = ['id', 'username', 'password', 'name', 'is_backofficer', 
                   'is_active', 'date_joined', 'address', 'birth',
                   'gender' ,'phone', 'email', 'last_login']
    user = dict(zip(user_fields, user_db_values))
    user.pop('password')
    user.pop('last_login')
    return user

def employee_db_convertor(employees_db_values):
    user_fields = ['id', 'username', 'password', 'name', 'is_backofficer', 
                   'is_active', 'date_joined', 'address', 'birth',
                   'gender' ,'phone', 'email', 'last_login']
    employee_fields = ['user_id', 'manager_id', 'vehicle_id', 'is_working', 'start_date', 'salary']
    user_fields.extend(employee_fields)

    employee_users = [
        dict(zip(user_fields, employee))
        for employee in employees_db_values
    ]
    
    return employee_users

def create_object(**attrs):
    return object().__dict__.update(attrs)