from django.core.files.base import ContentFile
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from six import BytesIO
from PIL import Image
import json


def create_image(storage, filename, size=(100, 100), image_mode='RGB', image_format='PNG'):
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)


class TestFileUpload(APITestCase):
    file_upload_url = '/message/file-upload'

    def test_file_upload(self):
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        data = {
            "file_upload": avatar_file
        }
        header = {"Content-Type: application/json; charset=UTF-8"}
        response = self.client.post(self.file_upload_url, data=data)
        result = response.json()
        print(result)
        expectation = f"https://meinchatapprepo.s3.amazonaws.com/media/font.png"
        self.assertEqual(response.status_code, 201)
        #self.assertEqual(result["file_upload"], expectation)
        self.assertEqual(result["id"], 1)


class TestMessage(APITestCase):
    message_url = '/message/message'
    file_upload_url = '/message/file-upload'

    def setUp(self):
        from user_control.models import CustomUser, UserProfile

        """sender"""
        self.sender = CustomUser.objects._create_user("sender", "sender123")
        UserProfile.objects.create(first_name="sender", last_name="hallo", user=self.sender)
        self.receiver = CustomUser.objects._create_user("receiver", "receiver123")
        UserProfile.objects.create(first_name="sender", last_name="hallo", user=self.receiver)
        """authenticate"""
        self.client.force_authenticate(user=self.sender)

    def test_post_message(self):
        payload = {
            "sender_id": self.sender.id,
            'receiver_id': self.receiver.id,
            "message":"mir geht es gut, welt, ich hore niemals auf, ich werde erfolgreich, sehen wir uns"
        }
        response= self.client.post(self.message_url, data=payload)
        result = response.json()
        print(result)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["message"], "mir geht es gut, welt, ich hore niemals auf, ich werde erfolgreich, sehen wir uns")
        self.assertEqual(result["sender"]["user"]["username"], "sender")

    def test_post_with_file(self):
        # create a file
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front1.png', avatar.getvalue())
        data = {
            "file_upload": avatar_file
        }
        response = self.client.post(
            self.file_upload_url, data=data)
        file_content = response.json()["id"]

        payload = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "message": "test message",
            "attachments": [
                {
                    "caption": "nice stuff",
                    "attachment_id": file_content
                },
                {
                    "attachment_id": file_content
                }
            ]
        }

        # processing
        response = self.client.post(self.message_url, data=json.dumps(
            payload), content_type='application/json')
        result = response.json()

        # assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["message"], "test message")
        self.assertEqual(result["sender"]["user"]["username"], "sender")
        self.assertEqual(result["receiver"]["user"]["username"], "receiver")
        self.assertEqual(result["message_attachments"]
                         [0]["attachment"]["id"], 1)
        self.assertEqual(result["message_attachments"]
                         [0]["caption"], "nice stuff")

    def test_update_message(self):

        # create message
        payload = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "message": "test message",

        }
        self.client.post(self.message_url, data=payload)

        # update message
        payload = {
            "message": "test message updated",
            "is_read": True
        }
        response = self.client.patch(
            self.message_url+"/1", data=payload)
        result = response.json()

        # assertions
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["message"], "test message updated")
        self.assertEqual(result["is_read"], True)

    def test_delete_message(self):

        # create message
        payload = {
            "sender_id": self.sender.id,
            "receiver_id": self.receiver.id,
            "message": "test message",

        }
        self.client.post(self.message_url, data=payload)

        response = self.client.delete(
            self.message_url+"/1", data=payload)

        # assertions
        self.assertEqual(response.status_code, 204)

    def test_get_message(self):
        response = self.client.get(self.message_url+f"?user_id={self.receiver.id}")
        result = response.json()

        self.assertEqual(response.status_code, 200)
