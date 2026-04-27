from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from uphirex.utils import api_response
from notifications.utils import create_notification
from .models import Connection
from .serializers import ConnectionSerializer


class ConnectionViewSet(viewsets.ModelViewSet):
    serializer_class = ConnectionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Connection.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).select_related('sender', 'receiver')

    def create(self, request, *args, **kwargs):
        receiver_id = request.data.get('receiver')
        if str(request.user.id) == str(receiver_id):
            return api_response(False, "Cannot connect with yourself.", status_code=status.HTTP_400_BAD_REQUEST)

        existing = Connection.objects.filter(
            Q(sender=request.user, receiver_id=receiver_id) |
            Q(sender_id=receiver_id, receiver=request.user)
        ).first()
        if existing:
            return api_response(False, "Connection already exists.", status_code=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conn = serializer.save(sender=request.user)

        # Notification for Receiver
        create_notification(
            user=conn.receiver,
            n_type='connection_request',
            from_user=request.user,
            message=f"{request.user.displayName or request.user.username} sent you a connection request.",
            reference_id=conn.id,
            reference_type='connection'
        )

        return api_response(True, "Connection request sent.", serializer.data, status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        conn = self.get_object()
        if conn.receiver != request.user:
            return api_response(False, "Only receiver can accept.", status_code=status.HTTP_403_FORBIDDEN)
        conn.status = Connection.Status.ACCEPTED
        conn.save(update_fields=['status', 'updated_at'])

        # Notification for Sender
        create_notification(
            user=conn.sender,
            n_type='connection_request',
            from_user=request.user,
            message=f"{request.user.displayName or request.user.username} accepted your connection request.",
            reference_id=conn.id,
            reference_type='connection'
        )

        return api_response(True, "Connection accepted.", ConnectionSerializer(conn).data, status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        conn = self.get_object()
        if conn.receiver != request.user:
            return api_response(False, "Only receiver can reject.", status_code=status.HTTP_403_FORBIDDEN)
        conn.status = Connection.Status.REJECTED
        conn.save(update_fields=['status', 'updated_at'])
        return api_response(True, "Connection rejected.", ConnectionSerializer(conn).data, status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        conn = self.get_object()
        if conn.sender != request.user and conn.receiver != request.user:
            return api_response(False, "Not part of this connection.", status_code=status.HTTP_403_FORBIDDEN)
        conn.status = Connection.Status.BLOCKED
        conn.save(update_fields=['status', 'updated_at'])
        return api_response(True, "Connection blocked.", ConnectionSerializer(conn).data, status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        pending = Connection.objects.filter(receiver=request.user, status='pending').select_related('sender')
        return api_response(True, "Pending connections.", ConnectionSerializer(pending, many=True).data, status.HTTP_200_OK)
