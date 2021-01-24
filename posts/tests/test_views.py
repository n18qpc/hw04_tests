import datetime

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.user = User.objects.create_user(username="test_user")
        cls.authorized_client = Client()
        cls.authorized_client.force_login(PagesTest.user)
        Group.objects.create(
            title="Тестовый заголовок группы",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        Group.objects.create(
            title="Тестовый заголовок группы2",
            description="Тестовое описание группы2",
            slug="test-slug2"
        )
        cls.post = Post.objects.create(
            text="Заголовок текстового поста",
            pub_date="20210121",
            author=PagesTest.user,
            group=Group.objects.get(slug="test-slug")
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "group.html": (
                reverse("group_posts", kwargs={"slug": "test-slug"})
            ),
            "new_post.html": reverse("new_post")
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        post_text_0 = response.context.get("page")[0].text
        post_pub_date_0 = response.context.get("page")[0].pub_date
        post_author_0 = response.context.get("page")[0].author
        post_group_0 = response.context.get("page")[0].group
        count_posts_paginator = len(response.context.get("page").object_list)
        self.assertEqual(post_text_0, "Заголовок текстового поста")
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, "test_user")
        self.assertEqual(post_group_0.slug, "test-slug")
        self.assertEqual(count_posts_paginator, 1)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("group_posts", kwargs={
            "slug": "test-slug"
        }))
        post_text_0 = response.context.get("page")[0].text
        post_pub_date_0 = response.context.get("page")[0].pub_date
        post_author_0 = response.context.get("page")[0].author
        post_group_0 = response.context.get("page")[0].group
        self.assertEqual(post_text_0, "Заголовок текстового поста")
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, "test_user")
        self.assertEqual(post_group_0.slug, "test-slug")

    def test_new_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("new_post"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f"value={value} {form_field} != {expected}"
                )

    def test_edit_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("post_edit", kwargs={
            "username": PagesTest.user.username,
            "post_id": PagesTest.post.id
        }))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field,
                    expected,
                    f"value={value} {form_field} != {expected}"
                )

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("profile", kwargs={
            "username": PagesTest.user.username
        }))
        post_text_0 = response.context.get("page")[0].text
        post_pub_date_0 = response.context.get("page")[0].pub_date
        post_author_0 = response.context.get("page")[0].author
        post_group_0 = response.context.get("page")[0].group
        self.assertEqual(post_text_0, "Заголовок текстового поста")
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, "test_user")
        self.assertEqual(post_group_0.slug, "test-slug")

    def test_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("post", kwargs={
            "username": PagesTest.user.username,
            "post_id": PagesTest.post.id
        }))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(
                    form_field, expected,
                    f"value={value} {form_field} != {expected}"
                )

    def test_post_with_group_in_index(self):
        response = self.authorized_client.get(reverse("index"))
        post_group_slug = response.context.get("page")[0].group.slug
        self.assertEqual(post_group_slug, "test-slug")

    def test_post_with_group_in_page_group(self):
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": "test-slug"})
        )
        post_group = response.context.get("page")[0].group.slug
        self.assertEqual(post_group, "test-slug")

    def test_post_with_group_unavailable_another_group(self):
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": "test-slug"})
        )
        post_group = response.context.get("page")[0].group.title
        self.assertNotEqual(post_group, "test-slug2")
