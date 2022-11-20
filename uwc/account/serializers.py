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
    name = serializers.CharField(required=False, default=None)
    address = serializers.CharField(required=False, default=None)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES,required=False, default=None)
    phone = serializers.CharField(required=False, default=None)
    email = serializers.EmailField(required=False, default=None)
    role = serializers.BooleanField()
    salary = serializers.IntegerField(required=False, default=None)
    birth = serializers.DateField(required=False, default=None)

class UpdateEmployeeSerializer(EmployeeSerializer):
    username = None
    password = None

    manager_id = serializers.IntegerField(required=False, default=None)
    vehicle_id = serializers.IntegerField(required=False, default=None)
    start_date = serializers.DateField(required=False, default=None)
    radius = serializers.DecimalField(max_digits=9, decimal_places=3,
                                      required=False, default=None)
    mcp_id = serializers.IntegerField(required=False, default=None)
    route_id =serializers.IntegerField(required=False, default=None)
    is_working = serializers.BooleanField(required=False, default=False)
