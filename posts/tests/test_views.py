import datetime

from django import forms
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from posts.forms import PostForm
from posts.models import Group, Post, User


class PagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.PAGE_NAME = "page"
        cls.test_username = "test_user"
        cls.user = User.objects.create_user(username=PagesTest.test_username)
        cls.authorized_client = Client()
        cls.anonymous_client = Client()
        cls.authorized_client.force_login(PagesTest.user)
        cls.group1 = Group.objects.create(
            title="Тестовый заголовок группы",
            description="Тестовое описание группы",
            slug="test-slug"
        )
        cls.group2 = Group.objects.create(
            title="Тестовый заголовок группы2",
            description="Тестовое описание группы2",
            slug="test-slug2"
        )
        cls.post = Post.objects.create(
            text="Заголовок текстового поста",
            pub_date="20210121",
            author=PagesTest.user,
            group=PagesTest.group1
        )

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            "index.html": reverse("index"),
            "group.html": (
                reverse("group_posts", kwargs={"slug": PagesTest.group1.slug})
            ),
            "new_post.html": reverse("new_post"),
            "about/author.html": reverse("about:author"),
            "about/tech.html": reverse("about:tech")
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("index"))
        post_text_0 = response.context.get(PAGE_NAME)[0].text
        post_pub_date_0 = response.context.get(PAGE_NAME)[0].pub_date
        post_author_0 = response.context.get(PAGE_NAME)[0].author
        post_group_0 = response.context.get(PAGE_NAME)[0].group
        count_posts_paginator = len(response.context.get(PAGE_NAME).object_list)
        self.assertEqual(post_text_0, PagesTest.post.text)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)
        self.assertEqual(count_posts_paginator, 1)

    def test_group_page_show_correct_context(self):
        response = self.authorized_client.get(reverse("group_posts", kwargs={
            "slug": PagesTest.group1.slug
        }))
        post_text_0 = response.context.get(PAGE_NAME)[0].text
        post_pub_date_0 = response.context.get(PAGE_NAME)[0].pub_date
        post_author_0 = response.context.get(PAGE_NAME)[0].author
        post_group_0 = response.context.get(PAGE_NAME)[0].group
        self.assertEqual(post_text_0, PagesTest.post.text)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

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
        post_text_0 = response.context.get(PAGE_NAME)[0].text
        post_pub_date_0 = response.context.get(PAGE_NAME)[0].pub_date
        post_author_0 = response.context.get(PAGE_NAME)[0].author
        post_group_0 = response.context.get(PAGE_NAME)[0].group
        self.assertEqual(post_text_0, PagesTest.post.title)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

    def test_post_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(PAGE_NAME, kwargs={
            "username": PagesTest.user.username,
            "post_id": PagesTest.post.id
        }))
        post_text_0 = response.context.get("post").text
        post_pub_date_0 = response.context.get("post").pub_date
        post_author_0 = response.context.get("post").author
        post_group_0 = response.context.get("post").group
        self.assertEqual(post_text_0, PagesTest.post.title)
        self.assertEqual(
            post_pub_date_0.strftime("%d %m %Y"),
            datetime.date.today().strftime("%d %m %Y")
        )
        self.assertEqual(post_author_0.username, PagesTest.test_username)
        self.assertEqual(post_group_0.slug, PagesTest.group1.slug)

    def test_post_with_group_in_index(self):
        response = self.authorized_client.get(reverse("index"))
        post_group_slug = response.context.get(PAGE_NAME)[0].group.slug
        self.assertEqual(post_group_slug, PagesTest.group1.slug)

    def test_post_with_group_in_page_group(self):
        response = self.authorized_client.get(
            reverse("group_posts", kwargs={"slug": PagesTest.group1.slug})
        )
        post_group = response.context.get(PAGE_NAME)[0].group.slug
        self.assertEqual(post_group, PagesTest.group1.slug)

    def test_post_with_group_unavailable_another_group(self):
        response = self.authorized_client.get(reverse("group_posts", kwargs={
            "slug": PagesTest.group2.slug
        }))
        post_group_slug = response.context.get(PAGE_NAME)[0].group.slug
        self.assertNotEqual(post_group_slug, PagesTest.group1.slug)

    def test_about_author_available_anonymous(self):
        response = self.anonymous_client.get(reverse_lazy("about:author"))
        status_code = response.status_code
        self.assertEqual(status_code, 404)

    def test_about_tech_available_anonymous(self):
        response = self.anonymous_client.get(reverse_lazy("about:tech"))
        status_code = response.status_code
        self.assertEqual(status_code, 404)

    def test_about_tech_show_correct_template(self):
        response = self.anonymous_client.get(reverse_lazy("about:tech"))
        self.assertTemplateUsed(response, template)

    def test_about_author_show_correct_template(self):
        response = self.anonymous_client.get(reverse_lazy("about:author"))
        self.assertTemplateUsed(response, template)
        self.assert

    def test_paginator_show_correct_posts_count(self):
        response = self.authorized_client.get(reverse("index"))
        count_posts_paginator = len(response.context.get(PAGE_NAME).object_list)
        self.assertEqual(count_posts_paginator, 1)
