from rest_framework.test import APITestCase
from .views import get_random,get_access_token, get_refresh_token
from .models import UserProfile, CustomUser
from message_control.tests import create_image, SimpleUploadedFile


class TesGenericFunction(APITestCase):

    def test_get_random(self):
        rand1 = get_random(10)
        rand2 = get_random(10)
        rand3 = get_random(15)

        self.assertTrue(rand1)
        self.assertNotEqual(rand1, rand2)
        self.assertEqual(len(rand3), 15)
        self.assertEqual(len(rand2), 10)

    def test_get_access_token(self):
        payload = {
            id: "1"
        }
        token = get_access_token(payload)
        self.assertTrue(token)

    def test_get_access_token(self):

        token = get_refresh_token()
        self.assertTrue(token)


class TestAuth(APITestCase):
    login_url = "/user/login"
    register_url = "/user/register"
    refresh_url = "/user/refresh"

    def test_register(self):
        payload = {
            "username": "parimah",
            "password": "4581077606",
            "email" : "ziayi@gmail.com"
        }
        response = self.client.post(self.register_url, data=payload)
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        payload = {
            "username": "parimah",
            "password": "4581077606",
            "email": "ziayi@gmail.com"
        }
        self.client.post(self.register_url, data=payload)
        response = self.client.post(self.login_url, data=payload)
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['access'])
        self.assertTrue(result['refresh'])

    def test_refresh(self):
        payload = {
            "username": "parimah",
            "password": "4581077606",
             "email": "ziayi@gmail.com"
        }
        self.client.post(self.register_url, data=payload)
        response = self.client.post(self.login_url, data=payload)
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(result['access'])
        self.assertTrue(result['refresh'])


class TestUserInfo(APITestCase):
    profile_url = '/user/profile'
    file_upload_url = '/message/file-upload'

    def setUp(self):
        self.user = CustomUser.objects._create_user(username="parimah", password="45689000")
       # UserProfile.objects.create(first_name="sender", last_name="hallo", user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_post_user_profile(self):
        payload = {
            "user_id": self.user.id,
            "first_name": "1",
            "last_name": "1",
            "caption": "3",
            "about": "rrr"
        }
        response = self.client.post(self.profile_url, data=payload)
        result = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["first_name"], "1")

    def test_file_upload_with_image(self):
        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        data = {
            "file_upload": avatar_file
        }
        header = {"Content-Type: application/json; charset=UTF-8"}
        response = self.client.post(self.file_upload_url, data=data)
        result = response.json()

        payload = {
            "user_id": self.user.id,
            "first_name": "1",
            "last_name": "1",
            "caption": "3",
            "about": "rrr",
            "profile_picture_id": result["id"]
        }
        response = self.client.post(self.profile_url, data=payload)
        result = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(result["first_name"], "1")
        self.assertEqual(result["user"]["username"], "parimah")
        self.assertEqual(result["profile_picture"]["id"], 1)

    def testـupdate_file_upload_with_image(self):

        avatar = create_image(None, 'avatar.png')
        avatar_file = SimpleUploadedFile('front.png', avatar.getvalue())
        data = {
            "file_upload": avatar_file
        }
        header = {"Content-Type: application/json; charset=UTF-8"}
        response = self.client.post(self.file_upload_url, data=data)
        image = response.json()

        payload = {
            "user_id": self.user.id,
            "first_name": "1",
            "last_name": "1",

        }

        response = self.client.post(self.profile_url, data=payload)
        result = response.json()

        payload = {
            "user_id": self.user.id,
            "first_name": "parimah",
            "about": "myabout"
        }

        response = self.client.patch(self.profile_url + f"/{result['id']}", data=payload)
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result["first_name"], "parimah")
        self.assertEqual(result["about"], "myabout")

    def test_user_search(self):
        UserProfile.objects.create(user=self.user,first_name="parimahjon", last_name="oseni")

        user2 = CustomUser.objects._create_user(username="farid", password="45689000")
        UserProfile.objects.create(first_name="faridjon", last_name="bonakdar", user=user2)

        user3 = CustomUser.objects._create_user(username="paria", password="45689000")
        UserProfile.objects.create(first_name="pariajon", last_name="ziaei", user=user3)

        url = self.profile_url + "?keyword=pari farid"
        response = self.client.get(url)
        result = response.json()["results"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["user"]["username"], "parimah")
        self.assertEqual(result[0]["message_count"], 0)





