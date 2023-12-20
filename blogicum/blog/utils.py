import datetime as dt

from django.shortcuts import get_object_or_404, redirect

from .models import Comment, Post


def post_filter(posts):
    return posts.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=dt.datetime.now(dt.timezone.utc)
    )


class PostMixin:
    template_name = 'blog/create.html'
    post_ = None

    def dispatch(self, request, *args, **kwargs):
        self.post_ = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        if self.post_.author == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return redirect('blog:post_detail', id=self.kwargs['post_id'])

    def get_object(self, queryset=None):
        return self.post_


class CommentMixin:
    template_name = 'blog/comment.html'
    post_ = None
    comment_ = None

    def dispatch(self, request, *args, **kwargs):
        self.post_ = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        self.comment_ = get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id']
        )
        if self.comment_.author == self.request.user:
            return super().dispatch(request, *args, **kwargs)
        return redirect(
            'blog:post_detail', id=self.kwargs['post_id']
        )

    def get_object(self, queryset=None):
        return self.comment_
