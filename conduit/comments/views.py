import json
import logging

from django.contrib.auth.decorators import (
    login_required,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.views.decorators.http import (
    require_http_methods,
)
from rest_framework import generics, status, permissions
from rest_framework.response import Response

from conduit.articles.models import Article
from conduit.comments.models import Comment
from conduit.comments.serializers import CommentSerializer
from conduit.comments.forms import CommentForm

logger = logging.getLogger(__name__)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        article_slug = self.kwargs['article_slug']
        return Comment.objects.filter(article__slug=article_slug)

    def create(self, request, article_slug=None, *args, **kwargs):
        article = get_object_or_404(Article, slug=article_slug)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, article=article)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDestroyAPIView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Comment.objects.all()

    def destroy(self, request, article_slug=None, pk=None, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk, article__slug=article_slug)
        if comment.author != request.user:
            return Response(
                {'errors': {'message': ['Not authorized']}},
                status=status.HTTP_403_FORBIDDEN
            )
        comment.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


@require_http_methods(["POST"])
@login_required
def add_comment(request: HttpRequest, article_id: int) -> HttpResponse:

    article = get_object_or_404(Article, pk=article_id)
    comment: Comment | None = None

    if (form := CommentForm(request.POST)).is_valid():

        comment = form.save(commit=False)
        comment.author = request.user
        comment.article = article
        comment.save()
        logger.info(f"Comment {comment} created")

        channel_layer = get_channel_layer()
        group_name = f"comments_{article_id}"
        logger.info(f"Send comment to group {group_name}")
        # Convert the comment data to JSON
        comment_data = {
            "id": comment.id,
            "content": comment.content,
            "author_id": comment.author.id,
            "html": json.dumps(
                render_to_string("comments/_comment.html", {"comment": comment})
            ),
        }

        # Send the comment JSON to the group
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment_message",
                "comment": comment_data,
            },
        )

        logger.info(f"Comment sent to group {group_name} with data: {comment_data}")

        # reset form
        form = CommentForm()

    return TemplateResponse(
        request,
        "comments/_comment_form.html",
        {
            "article": article,
            "form": form,
            "new_comment": comment,
        },
    )


@require_http_methods(["GET", "POST"])
@login_required
def edit_comment(request: HttpRequest, comment_id: int) -> HttpResponse:

    comment = get_object_or_404(
        Comment.objects.select_related("author"),
        author=request.user,
        pk=comment_id,
    )

    if request.method == "GET":

        return TemplateResponse(
            request,
            "comments/_comment_form.html",
            {
                "comment": comment,
                "form": CommentForm(instance=comment),
            },
        )

    if (form := CommentForm(request.POST, instance=comment)).is_valid():
        comment = form.save()

        return TemplateResponse(request, "comments/_comment.html", {"comment": comment})

    return TemplateResponse(
        request,
        "comments/_comment_form.html",
        {
            "comment": comment,
            "form": form,
        },
    )


@require_http_methods(["DELETE"])
@login_required
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    comment = get_object_or_404(
        Comment,
        author=request.user,
        pk=comment_id,
    )
    comment.delete()
    return HttpResponse()
