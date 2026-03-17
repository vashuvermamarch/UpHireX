from rest_framework import serializers
from .models import Connection


class ConnectionSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.displayName', read_only=True)
    receiver_name = serializers.CharField(source='receiver.displayName', read_only=True)

    class Meta:
        model = Connection
        fields = ('id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'status', 'created_at', 'updated_at')
        read_only_fields = ('id', 'sender', 'created_at', 'updated_at')
