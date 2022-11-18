from rest_framework import serializers

class LoginSerializer (serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class EmployeeSerializer(serializers.Serializer):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
    )
    username = serializers.CharField()
    password = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField()
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    phone = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.BooleanField()
    salary = serializers.IntegerField()
    birth = serializers.DateField()
    


