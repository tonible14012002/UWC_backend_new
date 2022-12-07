from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from .serializers import (
     LoginSerializer, 
     RefreshSerializer, 
     EmployeeSerializer,
     UpdateEmployeeSerializer,
     WorkTimeSerializer,
)
from django.conf import settings
from mysql import connector as mysql_connector
from .utils import (
    connect_db,
    user_db_convertor, 
    employee_db_convertor,
    create_object
    )
from .token import JWT_SECRET, JWT_ALGORITHM
from datetime import datetime
from datetime import timedelta
import jwt
from .token import auth_required

@api_view(("POST",))
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        credentials = serializer.data
        try:
            connection = connect_db()
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetUserFromLogin',(
                    credentials['username'],
                    credentials['password']
                    )
            )
            for tem in cursor.stored_results():
                user = tem.fetchall()[0]  # only get 1 user.
            connection.close()
            
            token = jwt.encode({'user_id' : user["id"], 
                                'exp' : datetime.utcnow() + timedelta(days=1),
                                'type': 'access'},
                                JWT_SECRET, 
                                JWT_ALGORITHM)
            refresh_token = jwt.encode({'user_id' : user["id"], 
                                        'exp' : datetime.utcnow() + timedelta(days=2),
                                        'type': 'refresh'},
                                        JWT_SECRET, 
                                        JWT_ALGORITHM)
            
            return Response({
                "user": user,
                "access": token,
                "refresh": refresh_token
            })

        except (mysql_connector.Error) as e:
            return Response({'detail': e.msg }, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def refresh(request):
    refresh_serializer = RefreshSerializer(data=request.data)
    if refresh_serializer.is_valid():
        token = refresh_serializer.data['refresh']
        payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        
        try:
            if (all(key in payload.keys() for key in ['user_id', 'type', 'exp']) 
                and payload['type'] == 'refresh'):
                payload['exp'] = datetime.utcnow() + timedelta(seconds=20)
                new_token = jwt.encode(payload,
                                        JWT_SECRET, 
                                        JWT_ALGORITHM)
                return Response({
                    "access": new_token
                }, status=status.HTTP_200_OK)
            return Response({"detail": "refresh token is invalid"})
        
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return Response({
                "detail": "Token is invalid or expired"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    return Response(refresh_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@auth_required
def employee(request):
    if request.method == 'GET':
        try:
            connection = mysql_connector.connect(**settings.DATABASE_CREDENTIALS)
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetEmployees', (request.user['id'],))
            for tem in cursor.stored_results():
                employees = tem.fetchall()
            for employee in employees:
                employee.pop('password')
                employee.pop('is_backofficer')
                employee.pop('user_id')
            connection.close()

        except mysql_connector.Error as e:
            return Response({"detail": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(employees, status=status.HTTP_200_OK)
    # POST method
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee_data = serializer.data
        try:
            connection = connect_db()
            cursor = connection.cursor()
            result = cursor.callproc('InsertEmployee', (
               None,
                employee_data['username'],
                employee_data['password'],
                employee_data['name'],
                request.user['id'],
                1,
                str(datetime.now()),
                employee_data['address'],
                employee_data['birth'],
                employee_data['gender'],
                employee_data['phone'],
                employee_data['email'],
                None,
                int(employee_data['role']),
                employee_data['salary']
            ))
            cursor.close()
            connection.commit()

            cursor = connection.cursor(dictionary=True)
            cursor.callproc('GetUser',(result[0],))
            for tem in cursor.stored_results():
                employee = tem.fetchall()
            connection.close()
            return Response(employee, status=status.HTTP_201_CREATED)
        except (mysql_connector.Error) as e:
            return Response({"detail": e.msg}, status=status.HTTP_400_BAD_REQUEST)
    return  Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@auth_required
def employee_detail(request, id):
    # Check id
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('GetUser',(id,))
        for tem in cursor.stored_results():
            employee = tem.fetchone()
        connection.close()
        if not employee:
            raise Http404

    # Get Method
        if request.method == 'GET':
            connection.reconnect()
            cursor = connection.cursor(dictionary=True)
            cursor.callproc('RetrieveSchedule',(id,))
            for tem in cursor.stored_results():
                schedule = tem.fetchall()
            employee['schedule'] = schedule

            connection.close()
            return Response(employee, status=status.HTTP_200_OK)
        # Put Method
        elif request.method == 'PUT':
            serializer = UpdateEmployeeSerializer(data=request.data)
            if serializer.is_valid():
                update_data = serializer.data
                update_fields_order = ('name', 'address', 'birth', 'gender', 'phone',
                                'email','manager_id', 'vehicle_id', 'start_date',
                                'radius', 'mcp_id', 'route_id', 'is_working', 'role', 'salary')
                connection.reconnect()
                cursor = connection.cursor(dictionary=True)
                cursor.callproc('UpdateEmployee', (id, *(update_data[field] for field in update_fields_order)))
                connection.commit()
                cursor.close()
                cursor = connection.cursor(dictionary=True)
                cursor.callproc('GetUser',(id,))
                for tem in cursor.stored_results():
                    employee_detail = tem.fetchall()
                connection.close()
                return Response(employee_detail, status=status.HTTP_200_OK)
            else:
                print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # Delete Method
        connection.reconnect()
        cursor = connection.cursor()
        cursor.callproc('DeleteEmployee',(id,))
        connection.commit()
        connection.close()

        return Response({'detail': 'success'}, status=status.HTTP_200_OK)
    except mysql_connector.Error as e:
        return Response({'detail': e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@auth_required
def schedule(request, employee_id):
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('GetUser',(employee_id,))
        for tem in cursor.stored_results():
            employee = tem.fetchone()
        if not employee:
            raise Http404
        cursor.close()
        connection.close()

        serializer = WorkTimeSerializer(data=request.data)
        if serializer.is_valid():
            worktime_data = serializer.data
            connection.reconnect()
            cursor = connection.cursor()
            result = cursor.callproc('InsertShift', (
                None,
                worktime_data['start_time'],
                worktime_data['end_time'],
                worktime_data['weekday'],
                employee_id
                ))
            cursor.close()
            connection.commit()

            cursor = connection.cursor(dictionary=True)
            cursor.callproc('RetrieveShift',(result[0],))
            for tem in cursor.stored_results():
                worktime = tem.fetchone()
            connection.close()
            return Response(worktime, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except mysql_connector.Error as e:
        return Response({'detail': e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'DELETE'])
@auth_required
def worktime_detail(request, employee_id, id):
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.callproc('GetUser', (employee_id,))
    for tem in cursor.stored_results():
        employee = tem.fetchone()
    if not employee:
        raise Http404
    connection.close()

    if request.method == 'GET':
        connection.reconnect()
        cursor = connection.cursor(dictionary=True)
        cursor.callproc('RetrieveShift',(id,))
        for tem in cursor.stored_results():
           worktime = tem.fetchone()
        connection.close()

        return Response(worktime, status=status.HTTP_200_OK)
    connection.reconnect()
    cursor = connection.cursor()
    cursor.callproc('DeleteShift', (id,))
    connection.commit()
    connection.close()

    return Response({'detail ': 'success'}, status=status.HTTP_200_OK)
