from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .serializers import GenericFileUploadSerializer, GenericFileUpload, MessageSerializer, Message, MessageAttachment
from rest_framework.permissions import IsAuthenticated
#from chatapi.custom_methods import IsAuthenticatedCustom
from rest_framework.response import Response
from django.db.models import Q
import requests
from django.conf import  settings
from chatapi.settings import SOCKET_SERVER
import json


def handleRequest(serializer):

    notification = {
        "message": serializer.data.get("message"),
        "from": serializer.data.get("sender"),
        "receiver": serializer.data.get("receiver"),
    }
    headers = {
        'Content-Type': 'application/json',
    }
    requests.post(settings.SOCKET_SERVER, json.dumps(notification), headers=headers)
    return True


class GenericFileUploadView(ModelViewSet):
    queryset = GenericFileUpload.objects.all()
    serializer_class = GenericFileUploadSerializer


class MessageView(ModelViewSet):
    """selected bara mostaghim va prefetch bara gheire moshtaghim relation"""
    queryset = Message.objects.select_related("sender", "receiver").prefetch_related("message_attachments")
    serializer_class = MessageSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        data = self.request.query_params.dict()
        user_id = data.get("user_id", None)
        if user_id:
            active_user_id = self.request.user.id
            return self.queryset.filter(Q(sender_id=user_id, receiver_id=active_user_id) | Q(receiver_id=active_user_id,
                                                                                       sender_id=user_id)).distinct()
        return self.queryset

    def create(self, request, *args, **kwargs):
        try:
            request.data._mutable = True
        except:
            pass
        attachments = request.data.pop("attachments", None)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #
        # if str(request.user.id) != request.data.get("sender_id", None):
        #     raise Exception("only sender can create a message")

        if attachments:
            MessageAttachment.objects.bulk_create(MessageAttachment(**attachment, message_id=serializer.data['id']) for attachment in attachments)
            message_data = self.get_queryset().get(id=serializer.data['id'])
            return Response(self.serializer_class(message_data).data, status=201)

        handleRequest(serializer)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        try:
            request.data._mutable = True
        except:
            pass
        attachments = request.data.pop("attachment", None)
        instance = self.get_object()
        serializer = self.serializer_class(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        MessageAttachment.objects.filter(message_id=instance.id).delete()

        if attachments:
            MessageAttachment.objects.bulk_create(MessageAttachment(**attachment, message_id=serializer.data['id']) for attachment in attachments)
            message_data = self.get_object()
            return Response(self.serializer_class(message_data).data, status=201)
        handleRequest(serializer)
        return Response(serializer.data, status=201)

