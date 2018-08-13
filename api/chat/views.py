from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import generics, viewsets
from rest_framework_extensions.mixins import NestedViewSetMixin

from api.chat import models, serializers


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer


class RoomViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Room.objects.all()
    serializer_class = serializers.RoomSerializer

    def get_queryset(self):
        user = self.request.user
        return user.room_set.all()


class MessageViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        parents_query_dict = self.get_parents_query_dict()
        room_id = parents_query_dict.get('room')
        user = self.request.user
        if not user.room_set.filter(id=room_id):
            raise Http404
        return super().get_queryset()
