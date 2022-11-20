from rest_framework import serializers

class MCPSerializer (serializers.Serializer):
    MCP_id = serializers.IntegerField()
    longtitude = serializers.DecimalField(10, 7)
    latitude = serializers.DecimalField(10, 7)
