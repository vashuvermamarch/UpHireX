from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    from_user_name = serializers.CharField(source='from_user.displayName', read_only=True, default='')

    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at')
