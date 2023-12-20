from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post, User
from .utils import CommentMixin, PostMixin, post_filter

POST_LIMIT = 10


class Index(ListView):
    template_name = 'blog/index.html'
    paginate_by = POST_LIMIT
    ordering = '-pub_date'
    queryset = post_filter(
        Post.objects.select_related(
            'category', 'location', 'author'
        )
    ).annotate(comment_count=Count('comments'))


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'

    def get_object(self, queryset=None):
        post = get_object_or_404(
            Post.objects.select_related(
                'category', 'location', 'author'
            ),
            pk=self.kwargs['id']
        )
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            post_filter(
                Post.objects.select_related(
                    'category', 'location', 'author'
                )
            ),
            pk=self.kwargs['id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPostsListView(ListView):
    template_name = 'blog/category.html'
    paginate_by = POST_LIMIT
    category = None

    def get_queryset(self):
        self.category = get_object_or_404(
            Category.objects.all(),
            Q(is_published=True) & Q(slug=self.kwargs['category_slug'])
        )
        post_list = post_filter(
            self.category.category_posts.select_related(
                'category', 'location', 'author'
            )
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        return post_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class ProfileListView(ListView):
    template_name = 'blog/profile.html'
    paginate_by = POST_LIMIT
    profile = None

    def get_queryset(self):
        self.profile = get_object_or_404(
            User,
            username=self.kwargs['username']
        )
        profile_posts = self.profile.posts_author.select_related(
            'category', 'location', 'author'
        ).annotate(comment_count=Count('comments')).order_by('-pub_date')
        if self.request.user.username == self.kwargs['username']:
            return profile_posts
        return post_filter(profile_posts)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.profile
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return User.objects.get(username=self.request.user)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.object}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, PostMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs['post_id']}
        )


class PostDeleteView(LoginRequiredMixin, PostMixin, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.post_)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile', kwargs={'username': self.post_.author}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    post_to_comment = None

    def dispatch(self, request, *args, **kwargs):
        self.post_to_comment = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_to_comment
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'id': self.kwargs['post_id']}
        )
