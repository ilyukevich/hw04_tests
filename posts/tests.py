# с тестами работал все ночь, поэтому думаю где-то перемудрил
# прошу понять и простить и за переменные в том числе:)
# постарался все ваши замечания исправить

from django.test import TestCase, Client
from .models import Group, Post, User
from django.urls import reverse


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client2 = Client()
        self.user = User.objects.create_user(username="sarah")
        self.user2 = User.objects.create_user(username="anonimus")
        self.group = Group.objects.create(title="titlejust", slug="just", description="description1")
        self.client.force_login(self.user)


    def search(self, post):
        """проверка наличия поста на всех нужных страницах"""
        # проверка, что новая запись появилась на всех связанных страницах
        value = post
        for url in (
            reverse("index"),
            reverse("profile", kwargs={"username": self.user}),
            reverse("post", kwargs={"username": self.user, "post_id": self.post.id}),
            reverse("group", kwargs={"slug": self.group.slug})
        ):
            response = self.client.get(url)
            self.assertContains(response, value)


    def check(self, post):
        """проверка всех полей из контекста"""
        post = Post.objects.get(author=self.user, id=self.post.id)
        value = post
        self.assertEqual(post.text, value.text)
        self.assertEqual(post.author, value.author)
        self.assertEqual(post.group, value.group)


    def test_personal_page(self):
        """After registering a user, his personal page (profile) is created"""
        response = self.client.get(reverse("profile", args=[self.user]))
        self.assertEqual(response.status_code, 200)

    # В тесте на публикацию поста авторизованным пользователем проверяем группу автора текст
    # и количество постов в базе. Проверяя количество постов в базе используем метод.count().
    def test_create_post_auth(self):
        """test_create_post"""
        # An authorized user can publish a post (new)
        posts_count_now = Post.objects.filter(author=self.user).count()
        self.post = Post.objects.create(
            text="just test text",
            author=self.user, group=self.group)
        posts_count_last = Post.objects.filter(author=self.user).count()
        self.assertEqual(posts_count_last, posts_count_now + 1)
        response = self.client.get(reverse("profile", args=[self.user]))
        self.assertEqual(len(response.context["author_posts"]), 1)
        self.assertContains(response, self.post.text)
        self.assertContains(response, self.post.group)
        # проверка наличия поста на всех нужных страницах
        value = self.post.text
        self.search(value)
        # проверка всех полей из контекста
        self.check(self.post)


    def test_create_post_unauth(self):
        """test_create_post"""
        # An unauthorized user can publish a post (new)
        posts_count_now = Post.objects.filter(author=self.user2).count()
        response = self.client2.post("/new/",
            text="just test text",
            author=self.user, group=self.group, follow=True)
        posts_count_last = Post.objects.filter(author=self.user).count()
        self.assertEqual(posts_count_last, posts_count_now)
        self.assertRedirects(response, '/auth/login/?next=/new/')


    def test_edit(self):
        self.post = Post.objects.create(
             text="just test text11111",
             author=self.user, group=self.group)
        response = self.client.post(
            reverse("post_edit",
                    kwargs={"username": self.user,
                            "post_id": self.post.id, }),
                    {'text': 'New text'})
        post_get = Post.objects.get(author=self.user, id=self.post.id)
        self.assertEqual(response.status_code, 302)
        value = post_get.text
        self.check(response)
