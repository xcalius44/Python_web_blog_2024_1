from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from .forms import CommentForm, EmailPostForm
from .models import Comment, Post

# Create your views here.

class PostListView(ListView):
    """Альтернативне подання списку постів"""
    queryset=Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Посторінкове розбиття з 3 постами на сторінку
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.page(1)
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts, 'tag': tag}
    )

def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    # Список активних коментарів до посту
    comments = post.comments.filter(active=True)
    # Форма для коментарів
    form = CommentForm()
    return render(
        request,
        'blog/post/detail.html',
        {'post': post, 'comments': comments, 'form': form}
    )

def post_share(request, post_id):
    # Отримати пост за id
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        # Форма передана на обробку
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Поля форми успішно пройшли валідацію
            cd = form.cleaned_data
            # відправити електронного листа
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']}  рекомендує Вам прочитати {post.title}"
            message = f"Прочитай {post.title} за покликанням {post_url}\n\n" \
                      f"Коментар від {cd['name']}: {cd['comments']}"
            send_mail(subject, message, 'blog@mail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # Коментар було відправлено
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Створити об'єкт Comment, не зберігаючи його в БД
        comment = form.save(commit=False)
        # Призначити пост коментарю
        comment.post = post
        # Зберегти коментар в БД
        comment.save()
    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})