from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


class PostModelTest(TestCase):
    def setUp(self):
        post = Post.objects.create(
            text="Заголовок тестовой задачи",
            pub_date="2020-05-12",
            author=get_user_model().objects.create(username="testuser")
        )
        group = Group.objects.create(
            title="Заголовок тестовой группы",
            slug="testgroup",
            description="Тестовое описание группы"
        )
        self.group = group
        self.post = post

    def test_text_verbose_name(self):
        verbose_name = self.post._meta.get_field("text").verbose_name
        self.assertEquals(verbose_name, "Текст сообщения")

    def test_text_help_text(self):
        help_text = self.post._meta.get_field("text").help_text
        self.assertEquals(help_text, "Введите текст")

    def test_post_str(self):
        post_text = self.post.text[:50]
        date = self.post.pub_date
        self.assertEquals(
            str(self.post),
            f"{date} {self.post.author} {self.post.group} {post_text}"
        )

    def test_group_str(self):
        self.assertEquals(str(self.group), "Заголовок тестовой группы")
