import jwt
from rest_framework.response import Response
from rest_framework import status
from mysql import connector as mysql_connector
from django.conf import settings
from .utils import (
    user_db_convertor,
    connect_db
)

JWT_SECRET = 'secret'
JWT_ALGORITHM = 'HS256'
JWT_EXP_DELTA_SECONDS = 20

def auth_required(func):
    def token_required_view(request, *args, **kwargs):
        bearer = request.headers.get("Authorization", None)
        if not bearer:
            return Response({
                "message": "Authorization required, missing bearer token."
            }, status= status.HTTP_400_BAD_REQUEST)
        try:
            token = bearer.split(" ")[1]
            payload = jwt.decode(token, JWT_SECRET, JWT_ALGORITHM)
        
            if (all(key in payload.keys() for key in ['user_id', 'type', 'exp']) 
                and payload['type'] == 'access'):
                
                user_id = payload.get('user_id')
                connection = connect_db()
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    f"""
                    CALL GetUser({user_id})
                    """
                )
                user =  cursor.fetchall()[0]
                if not user['is_backofficer']:
                    return Response(
                        {"message": "This is not back officer account"}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                request.user = user
        except (mysql_connector.Error) as e:
            return Response({
                "message": e.msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            return Response({
                "message": "Token is invalid or expired"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        return func(request, *args, **kwargs)

    return token_required_view


