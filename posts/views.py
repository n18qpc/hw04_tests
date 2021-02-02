from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POSTS_PER_PAGE = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
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
    return render(request, "new_post.html", {
        "form": form,
        "is_edit": False,
        "username": request.user.username
    })


def profile(request, username):
    author = User.objects.get(username=username)
    posts = Post.objects.select_related("author").filter(
        author__username=username
    )
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(request, "profile.html", {
        "author": author,
        "page": page,
        "paginator": paginator,
        "count_posts": posts.count
    })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    count_posts = post.author.posts.count
    return render(
        request,
        "post.html",
        {
            "post": post,
            "count_posts": count_posts,
            "author": author
        }
    )


@login_required
def post_edit(request, username, post_id):
    post_edit = get_object_or_404(Post, id=post_id)
    if request.user.username != username:
        return redirect("post", username, post_id)
    form = PostForm(request.POST or None, instance=post_edit)
    if form.is_valid():
        post_form = form.save(commit=False)
        post_edit.text = post_form.text
        post_edit.group = post_form.group
        post_edit.save()
        return redirect("post", username, post_id)
    else:
        return render(request, "new_post.html", {
            "username": username,
            "post_id": post_id,
            "is_edit": True,
            "form": form,
            "post_edit": post_edit,
        })
