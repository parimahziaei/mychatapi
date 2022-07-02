from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import GenericFileUpload, Message, MessageAttachment


class GenericFileUploadSerializer(ModelSerializer):
    class Meta:
        model = GenericFileUpload
        fields = "__all__"


class MessageAttachmentSerializer(ModelSerializer):
    attachment = GenericFileUploadSerializer()

    class Meta:
        model = MessageAttachment
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    """barae circle bodane ralation"""
    sender = serializers.SerializerMethodField
    sender = serializers.SerializerMethodField("get_sender_data")
    sender_id = serializers.IntegerField(write_only=True)
    receiver = serializers.SerializerMethodField("get_receiver_data")
    receiver_id = serializers.IntegerField(write_only=True)
    """inja chon az ye jadval di avorde pas many=true mishe"""
    message_attachments = MessageAttachmentSerializer(read_only=True, many=True)

    class Meta:
        model = Message
        fields = "__all__"

    def get_sender_data(self, obj):
        from user_control.serializers import UserProfileSerializer
        return UserProfileSerializer(obj.sender.user_profile).data

    def get_receiver_data(self, obj):
        from user_control.serializers import UserProfileSerializer
        return UserProfileSerializer(obj.receiver.user_profile).data



