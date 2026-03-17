from rest_framework import serializers
from .models import ChatRoom, ChatParticipant, Message, MessageRead


class ChatRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatRoom
        fields = '__all__'
        read_only_fields = ('id', 'created_at')


class ChatParticipantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    displayName = serializers.CharField(source='user.displayName', read_only=True)

    class Meta:
        model = ChatParticipant
        fields = ('room', 'user', 'username', 'displayName', 'joined_at', 'last_seen', 'notification_enabled')
        read_only_fields = ('joined_at',)


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.displayName', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ('id', 'sender', 'created_at')


class MessageReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageRead
        fields = ('message', 'user', 'read_at')
        read_only_fields = ('read_at',)
