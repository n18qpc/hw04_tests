from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Post, User


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text="Текст тестового поста",
            author=self.user
        )

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовый текст"
        }
        response = self.authorized_client.post(
            reverse("new_post"),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse("index"))
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertTrue(
            Post.objects.filter(text="Тестовый текст").exists()
        )

    def test_edit_post(self):
        form_data = {"text": "Измененный текст"}
        self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={
                    "username": self.user.username,
                    "post_id": self.post.id
                }
            ),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, "Измененный текст")
