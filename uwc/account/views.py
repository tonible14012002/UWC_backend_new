from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
     LoginSerializer, 
     RefreshSerializer, 
     EmployeeSerializer,
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
        user=None
        try:
            connection = connect_db()
            cursor = connection.cursor()
            cursor.execute(
                f"""
                CALL `GetUserFromLogin`(
                    '{credentials['username']}',
                    '{credentials['password']}'
                    )
                """
            )
            user = user_db_convertor(cursor.fetchall()[0])  # only get 1 user.
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
            return Response({'message': e.msg }, status=status.HTTP_400_BAD_REQUEST)
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
            return Response({"message": "refresh token is invalid"})
        
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return Response({
                "message": "Token is invalid or expired"
            }, status=status.HTTP_400_BAD_REQUEST)
            
    return Response(refresh_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@auth_required
def employee(request):
    if request.method == 'GET':
        try:
            connection = mysql_connector.connect(**settings.DATABASE_CREDENTIALS)
            cursor = connection.cursor()
            cursor.execute(
                f"""
                CALL GetEmployees({request.user['id']})
                """
            )
            employees = employee_db_convertor(cursor.fetchall())
            connection.close()
        except mysql_connector.Error as e:
            return Response({"message": e.msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(employees, status=status.HTTP_200_OK)
    # POST method
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee_data = serializer.data
        try:
            connection = connect_db()
            cursor = connection.cursor()
            cursor.execute(
                f"""
                CALL InsertEmployee(NULL,
                '{employee_data['username']}',
                sha2('{employee_data['password']}',0),
                '{employee_data['name']}',
                {request.user['id']},
                1,
                SYSDATE(),
                '{employee_data['address']}',
                '{employee_data['birth']}',
                '{employee_data['gender']}',
                '{employee_data['phone']}',
                '{employee_data['email']}',
                NULL,
                {int(employee_data['role'])},
                {employee_data['salary']});
                """
            )
            connection.commit()
            connection.close()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except (mysql_connector.Error) as e:
            return Response({"message": e.msg}, status=status.HTTP_400_BAD_REQUEST)
    return  Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def employee_detail(request, id):
    return Response({})


