from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name="Текст сообщения",
        help_text="Введите текст"
    )
    pub_date = models.DateTimeField(
        "date published",
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу"
    )

    def __str__(self):
        short_text = self.text[:50]
        return f"{self.pub_date} {self.author} {self.group} {short_text}"

    class Meta:
        ordering = ("-pub_date",)
