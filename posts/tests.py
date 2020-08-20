# благодарен за ревью всего этого)


from django.test import TestCase, Client
from .models import Group, Post, User
from django.urls import reverse


class ProfileTest(TestCase):
    def setUp(self):
        self.auth_client = Client()
        self.unauth_client = Client()
        self.user_auth = User.objects.create_user(username="sarah")
        self.user_unauth = User.objects.create_user(username="anonimus")
        self.group = Group.objects.create(title="titlejust", slug="just", description="description1")
        self.auth_client.force_login(self.user_auth)


    def search_text_page(self, text):
        """checking the presence of a post on all the necessary pages
        (new entry appeared on all linked pages)"""

        search_text = text
        for url in (
            reverse("index"),
            reverse("profile", kwargs={"username": self.user_auth}),
            reverse("post", kwargs={"username": self.user_auth, "post_id": self.post.id}),
            reverse("group", kwargs={"slug": self.group.slug})
        ):
            response = self.auth_client.get(url)
            self.assertContains(response, search_text)


    def check_fields(self, post_text):
        """checking all fields from context"""

        post_get = Post.objects.get(author=self.user_auth, id=self.post.id)
        value = post_text
        self.assertEqual(post_get.text, value)
        self.assertEqual(post_get.author, self.user_auth)
        self.assertEqual(post_get.group, self.group)


    def test_personal_page(self):
        """After registering a user, his personal page (profile) is created"""

        response = self.auth_client.get(reverse("profile", args=[self.user_auth]))
        self.assertEqual(response.status_code, 200)


    def test_create_post_auth(self):
        """test_create_post
        An authorized user can publish a post (new),
        check the author's group, text and number of posts in the database"""

        self.text_new = "just test text"
        posts_count_now = Post.objects.filter(author=self.user_auth).count()
        self.post = Post.objects.create(
            text=self.text_new,
            author=self.user_auth, group=self.group)
        posts_count_last = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(posts_count_last, posts_count_now + 1)
        response = self.auth_client.get(reverse("profile", args=[self.user_auth]))
        self.assertEqual(len(response.context["author_posts"]), 1)
        self.assertContains(response, self.post.text)
        self.assertContains(response, self.post.group)

        # check if a post is present on all required pages
        self.search_text_page(self.text_new)

        # checking all fields from context
        self.check_fields(self.text_new)


    def test_create_post_unauth(self):
        """test_create_post
        An unauthorized user can publish a post (new)"""
        test_text = "Python"
        posts_count_now = Post.objects.filter(author=self.user_unauth).count()
        response = self.unauth_client.post(reverse('new_post'),
                                    {'text': test_text, 'author': self.user_unauth,
                                     'group': self.group.id}, follow=True)
        posts_count_last = Post.objects.filter(author=self.user_unauth).count()
        self.assertEqual(posts_count_last, posts_count_now)
        self.assertRedirects(response, f"{reverse('login')}?next=/new/")


    def test_edit(self):
        """test_edit_post
                An authorized user can edit a post"""
        self.text_create = "Old just test text11111"
        self.text_edit = "New text11111"
        self.post = Post.objects.create(
             text=self.text_create,
             author=self.user_auth, group=self.group)
        post_now = Post.objects.filter(author=self.user_auth).count()
        response = self.auth_client.post(
            reverse("post_edit",
                    kwargs={"username": self.user_auth,
                            "post_id": self.post.id, }),
                    {'text': self.text_edit, 'group': self.group.id})
        self.assertEqual(response.status_code, 302)
        post_update = Post.objects.filter(author=self.user_auth).count()
        self.assertEqual(post_now, post_update)
        self.search_text_page(self.text_edit)
        self.check_fields(self.text_edit)
