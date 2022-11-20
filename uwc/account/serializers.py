from rest_framework import serializers
from datetime import time, datetime, date

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

class WorkTimeSerializer(serializers.Serializer):
    WEEKDAY_CHOICES = (
        ('Mon', 'Monday'),
        ('Tue', 'Tuesday'), 
        ('Wed', 'Wednesday'), 
        ('Thur', 'Thursday'),
        ('Fri', 'Friday'),
        ('Sat', 'Satuday'),
        ('Sun', 'Sunday'),
    )
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')
    weekday = serializers.ChoiceField(choices=WEEKDAY_CHOICES)

    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']

        temp_date = date(1,1,1)

        time_interval = (datetime.combine(temp_date, end_time) 
                         - datetime.combine(temp_date, start_time))
        if time_interval.total_seconds() <= 0:
            raise serializers.ValidationError('Invalid work time.')
        return data


