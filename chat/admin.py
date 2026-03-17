from django.contrib import admin
from .models import ChatRoom, ChatParticipant, Message, MessageRead


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'created_at', 'last_message_at')
    list_filter = ('type',)
    search_fields = ('name',)


@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('room', 'user', 'joined_at', 'last_seen')
    search_fields = ('user__username',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'message_type', 'content', 'created_at')
    list_filter = ('message_type',)
    search_fields = ('sender__username', 'content')


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'read_at')
    search_fields = ('user__username',)
