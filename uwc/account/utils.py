

def user_db_convertor(user_db_fields):
    user_fields = ['id', 'username', 'password', 'name', 'is_backofficer', 
                   'is_active', 'date_joined', 'address', 'birth',
                   'gender' ,'phone', 'email', 'last_login']
    return dict(zip(user_fields, user_db_fields))
