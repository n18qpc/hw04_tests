from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "pub_date", "author")
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"
    search_fields = ("text", "author")


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    list_filter = ("title", "slug")
    empty_value_display = "-пусто-"
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
