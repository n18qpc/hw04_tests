from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title="Тестовый заголовок группы",
            description="Тестовое описание группы",
            slug="test-slug"
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = get_user_model().objects.create_user(username="testuser")
        User = get_user_model()
        self.user_author = User.objects.create_user(username="userauthor")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text="Текст тестового поста",
            author=self.user
        )
        self.post_author = Post.objects.create(
            text="Текст тестового поста",
            author=self.user_author
        )
        self.url_names_authorized = {
            "/": 200,
            "/about/tech/": 200,
            "/about/author/": 200,
            "/new/": 200,
            "/group/test-slug/": 200,
            f"/{self.user.username}/": 200,
            f"/{self.user.username}/{self.post.id}/": 200,
            f"/{self.user.username}/{self.post.id}/edit/": 200,
            f"/{self.user_author.username}/{self.post_author.id}/edit/": 302,
        }
        self.url_names_anonymous = {
            "/": 200,
            "/about/tech/": 200,
            "/about/author/": 200,
            "/new/": 302,
            "/group/test-slug/": 200,
            f"/{self.user.username}/": 200,
            f"/{self.user.username}/{self.post.id}/edit/": 302
        }
        self.templates_url_names = {
            "index.html": "/",
            "group.html": "/group/test-slug/",
            "new_post.html": "/new/",
            "new_post.html": f"/{self.user.username}/{self.post.id}/edit/",
            "about/author.html": "/about/author/",
            "about/tech.html": "/about/tech/",
        }

    def test_urls_correct_status_code(self):
        for url, status_code in self.url_names_authorized.items():
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, status_code)
        for url, status_code in self.url_names_anonymous.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    status_code
                )

    def test_urls_uses_correct_templates(self):
        for template, reverse_name in self.templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(
                    response,
                    template
                )
