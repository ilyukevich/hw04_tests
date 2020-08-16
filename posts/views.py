from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def index(request):
    latest = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(latest, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(
        request,
        'index.html',
        {'posts': latest, 'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    """view function for community page"""
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"group": group, "page": page, "paginator": paginator}
    )


# revision2
# close pages from unauthorized users
@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.save()
            return redirect('/')

    form = PostForm()
    return render(request, 'new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    # тут тело функции. Не забудьте проверить,
    # что текущий пользователь — это автор записи.
    # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
    # который вы создали раньше (вы могли назвать шаблон иначе)
    profile = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    if profile != request.user:
        return redirect("post", username=post.author, post_id=post_id)
    else:
        if request.method == 'POST':
            form = PostForm(request.POST)
            if form.is_valid():
                edit_post = form.save(commit=False)
                edit_post.author = post.author
                edit_post.id = post.id
                edit_post.pub_date = post.pub_date
                edit_post.save()
                return redirect("post", username=post.author, post_id=post_id)
        else:
            form = PostForm(instance=post)
        context = {
            "form": form,
            "post": post,
            "username": username,
            "post_id": post_id,
            }
        return render(request, "new.html", context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=author).count()
    author_posts = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(author_posts, 6)
    page = paginator.get_page(request.GET.get('page'))
    return render(request, 'profile.html', {
        'page': page,
        'paginator': paginator,
        'posts_count': posts_count,
        'author': author,
        'author_posts': author_posts,
    })


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author.id, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    return render(request, 'post.html', {
        'posts_count': posts_count,
        'post': post,
        'author': author,
    })

# @login_required
# def post_edit(request, username, post_id):
#     # тут тело функции. Не забудьте проверить,
#     # что текущий пользователь — это автор записи.
#     # В качестве шаблона страницы редактирования укажите шаблон создания новой записи
#     # который вы создали раньше (вы могли назвать шаблон иначе)
#     profile = get_object_or_404(User, username=username)
#     post = get_object_or_404(Post, id=post_id)
#     if profile == post.author:
#         if request.method == 'POST':
#             form = PostForm(request.POST)
#             if form.is_valid():
#                 edit_post = form.save(commit=False)
#                 edit_post.author = post.author
#                 edit_post.id = post.id
#                 edit_post.pub_date = post.pub_date
#                 edit_post.save()
#                 return redirect("/")
#     form = PostForm()
#     context = {
#         "form": form,
#         "post": post,
#         "username": username,
#         "post_id": post_id,
#     }
#     return render(request, "new.html", context)



