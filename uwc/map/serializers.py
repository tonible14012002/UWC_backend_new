from rest_framework import serializers
import json
from decimal import *

class MCPSerializer (serializers.Serializer):
    MCP_id = serializers.IntegerField()
    longtitude = serializers.DecimalField(10, 7)
    latitude = serializers.DecimalField(10, 7)