from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import (
     LoginSerializer, 
     RefreshSerializer
)
from django.conf import settings
from mysql import connector as mysql_connector
from .utils import user_db_convertor
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
            connection = mysql_connector.connect(**settings.DATABASE_CREDENTIALS)
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
                                'exp' : datetime.utcnow() + timedelta(seconds=20),
                                'type': 'access'},
                                JWT_SECRET, 
                                JWT_ALGORITHM)
            refresh_token = jwt.encode({'user_id' : user["id"], 
                                        'exp' : datetime.utcnow() + timedelta(days=1),
                                        'type': 'refresh'},
                                        JWT_SECRET, 
                                        JWT_ALGORITHM)
            
            return Response({
                "user": user,
                "access": token,
                "refresh": refresh_token
            })

        except (mysql_connector.Error, Exception) as e:
            return Response({'message': e.msg}, status=status.HTTP_400_BAD_REQUEST)
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

@api_view(["GET"])
@auth_required
def home(request):
    print(request.user)
    return Response({"message":"success"})

# Create your views here.
