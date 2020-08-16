# from django.test import TestCase
#
#
# class TestStringMethods(TestCase):
#     def test_length(self):
#                 self.assertEqual(len('yatube'), 6)
#
#     def test_show_msg(self):
#                 # действительно ли первый аргумент — True?
#                 self.assertTrue(False, msg="Важная проверка на истинность")

from django.test import TestCase, Client

from .models import User


class TestProfile(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@testmail.by",
            password="testpass",
        )

    def test_profile(self):
        user_profile = self.client.get("/testuser/")
        self.assertEqual(
            user_profile.status_code,
            200,
            msg="Профиль пользователя после регистрации не создаётся",
        )
        self.assertTemplateUsed(user_profile, "profile.html")
        self.assertContains(user_profile, "testuser")

    def test_new_post(self):
        self.client.login(username="testuser", password="testpass")
        new_post = self.client.get("/new/", follow=True)
        self.assertEqual(
            new_post.status_code,
            200,
            msg="Авторизованный юзер не может создать новый пост",
        )
        self.assertTemplateUsed(new_post, "new_post.html")
        self.client.logout()
        index = self.client.get("/")
        self.assertNotContains(index, "testuser")
        self.assertRedirects(
            new_post, "http://testserver/auth/login/?next=/new/"
        )
        self.assertTemplateNotUsed(new_post, "new_post.html")
        self.assertTemplateUsed(new_post, "login.html")