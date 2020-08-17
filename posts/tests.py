from django.test import TestCase, Client
from .models import Post, User
from django.urls import reverse


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="sarah",
            email="connor.s@skynet.com",
            password="12345"
        )
        self.post = Post.objects.create(
            text="test_text",
            author=self.user
        )


    def test_personal_page(self):
        """After registering a user, his personal page (profile) is created"""
        profile = self.client.get("/sarah/")
        self.assertEqual(profile.status_code, 200)
        self.assertContains(profile, "sarah")


    def test_create_post(self):
        """test_create_post"""
        # An authorized user can publish a post (new)
        self.client.post('/auth/login/', {'username': 'sarah', 'password': '12345'})
        new_post = self.client.get("/new/", follow=True)
        self.assertEqual(new_post.status_code, 200)
        self.assertTemplateUsed(new_post, "new.html")

        # An unauthorized visitor cannot publish a post (it is redirected to the login page)
        self.client.logout()
        response = self.client.get("/new/")
        self.assertRedirects(response, '/auth/login/?next=/new/')


    def test_publication(self):
        """After the post is published, a new post appears on the main page of the site (index), on the user's
        personal page (profile), and on a separate post page (post)"""
        response = self.client.get("/")
        self.assertContains(response, self.post.text)
        response = self.client.get(reverse("profile", args=[self.user.username]))
        self.assertContains(response, self.post.text)
        response = self.client.get(reverse("post", args=[self.user.username, self.post.id]))
        self.assertContains(response, self.post.text)


    def test_edit(self):
        """An authorized user can edit his post and its content will change on all linked pages"""
        self.client.post('/auth/login/', {'username': 'sarah', 'password': '12345'})
        self.client.post(reverse("post_edit", args=[self.user.username, self.post.id]), {"text": "GOOD"})
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GOOD")
        response = self.client.get("/sarah/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GOOD")
        response = self.client.get("/sarah/1/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "GOOD")
