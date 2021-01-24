from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import PostForm
from .models import Group, Post


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    context = {
        "group": group,
        "page": page,
        "paginator": paginator
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("index")
    return render(request, "new_post.html", {"form": form, "is_edit": False})


def profile(request, username):
    author = get_user_model().objects.get(username=username)
    posts = Post.objects.select_related("author").filter(author__username=username)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {
        "author": author,
        "posts": posts,
        "page": page,
        "post": Post,
        "paginator": paginator
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = get_user_model().objects.get(username=username)
    count_posts = Post.objects.select_related("author").filter(
        author__username=username
    ).count
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
    else:
        form = PostForm(instance=post)
    return render(
        request,
        "post.html",
        {
            "form": form,
            "post": post,
            "count_posts": count_posts,
            "author": author
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user.username == username:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect(reverse(
                    "post",
                    kwargs={
                        "username": username,
                        "post_id": post_id
                    }
                ))
        else:
            form = PostForm(instance=post)
    else:
        return redirect(reverse("post", kwargs={
            "username": username,
            "post_id": post_id
        }))
    context = {"form": form, "is_edit": True, "post": post}
    return render(request, "new_post.html", context)
