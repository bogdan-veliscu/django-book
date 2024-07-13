import logging

from articles.filters import ArticleFilter
from articles.models import Article
from articles.serializers import ArticleSerializer, TagSerializer
from comments.forms import CommentForm
from comments.models import Comment
from django.core.cache import cache
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView
from profiles.models import User
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from taggit.models import Tag

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ArticleViewSet(viewsets.ModelViewSet):
    queryset = (
        Article.objects.select_related("author").prefetch_related("favorites").all()
    )
    serializer_class = ArticleSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "slug"
    filterset_class = ArticleFilter
    http_method_names = ["get", "post", "put", "delete"]

    def get_permissions(self):
        if self.action == "retrieve" or self.action == "list":
            return [IsAuthenticatedOrReadOnly()]

        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        try:
            article_data = request.data.get("article", {})
            logger.debug(f"Create article with data: {article_data}")
            serializer = self.get_serializer(data=article_data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            logger.debug(f"Headers: {headers}")
            return Response(
                {"article": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )

        except Exception as e:
            logger.error(e)
            return Response(
                {
                    "errors": {
                        "body": ["Bad request: unable to create article"],
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post", "delete"])
    def favorite(self, request, slug=None):
        logger.debug(f"### Favorite request: {request}")
        if request.method == "POST":
            try:
                article = Article.objects.get(slug=slug)
                if article.favorites.filter(pk=request.user.pk).exists():
                    return Response(
                        {"errors": {"body": ["Article already favorited"]}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                article.favorites.add(request.user)
                serializer = self.get_serializer(article)

                return Response(
                    {"article": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Article.DoesNotExist:
                return Response(
                    {"errors": {"body": ["Article not found"]}},
                    status=status.HTTP_404_NOT_FOUND,
                )
        elif request.method == "DELETE":
            try:
                article = Article.objects.get(slug=slug)
                if not article.favorites.filter(pk=request.user.pk).exists():
                    return Response(
                        {"errors": {"body": ["Article not favorited"]}},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                article.favorites.remove(request.user)
                serializer = self.get_serializer(article)

                return Response(
                    {"article": serializer.data},
                    status=status.HTTP_200_OK,
                )
            except Article.DoesNotExist:
                return Response(
                    {"errors": {"body": ["Article not found"]}},
                    status=status.HTTP_404_NOT_FOUND,
                )

    @action(detail=False)
    def feed(self, request, *args, **kwargs):
        try:
            logger.info(f"Feed request: {request}.user: {request.user}")
            followed_authors = User.objects.filter(followers=request.user)
            queryset = self.get_queryset()
            logger.debug(f"Feed followed authors: {followed_authors}")
            articles = queryset.filter(author__in=followed_authors).order_by("-created")
            logger.info(f"Feed articles: {articles}")
            queryset = self.filter_queryset(articles)
            logger.debug(f"Feed Queryset: {queryset}")
            serializer = self.get_serializer(queryset, many=True)
            response = {
                "articles": serializer.data,
                "articlesCount": queryset.count(),
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"errors": {"body": ["Bad request: unable to retrieve feed articles"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False)
    def recent(self, request, *args, **kwargs):
        try:
            if "recent_articles" not in cache:
                queryset = self.get_queryset()
                articles = queryset.order_by("-created")[:5]
                serializer = self.get_serializer(articles, many=True)
                articles = serializer.data
                cache.set("recent_articles", articles, 60 * 60)
            else:
                articles = cache.get("recent_articles")

            return Response(
                {"articles": articles},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {
                    "errors": {
                        "body": ["Bad request: unable to retrieve recent articles"]
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = queryset.get(slug=slug)
            serializer = self.get_serializer(article)

            return Response(
                {"article": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Article.DoesNotExist:
            return Response(
                {"errors": {"body": ["Article not found"]}},
                status=status.HTTP_404_NOT_FOUND,
            )

    def update(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = queryset.get(slug=slug)
            if article.author != request.user:
                return Response(
                    {"errors": {"body": ["Permission denied"]}},
                    status=status.HTTP_403_FORBIDDEN,
                )

            article_data = request.data.get("article", {})
            serializer = self.get_serializer(article, data=article_data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(
                {"article": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Article.DoesNotExist:
            return Response(
                {"errors": {"body": ["Article not found"]}},
                status=status.HTTP_404_NOT_FOUND,
            )

    def destroy(self, request, slug, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            article = Article.objects.get(slug=slug)
            if article.author != request.user:
                return Response(
                    {"errors": {"body": ["Unauthorized access"]}},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            self.perform_destroy(article)

            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )
        except Article.DoesNotExist:
            return Response(
                {"errors": {"body": ["Article not found: unable to delete article"]}},
                status=status.HTTP_404_NOT_FOUND,
            )


class TagView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    http_method_names = ["get"]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            tags = [element.name for element in queryset]
            serializer = self.get_serializer({"tagList": tags})

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"errors": {"body": ["Bad request: unable to retrieve tags"]}},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ArticleCreateView(CreateView):
    model = Article
    template_name = "articles/article_form.html"
    fields = ["title", "summary", "content"]
    success_url = reverse_lazy("articles:article_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


from django.http import JsonResponse
from django.template.loader import render_to_string


class ArticleListView(ListView):
    model = Article
    template_name = "articles/home.html"
    context_object_name = "articles"
    paginate_by = 3

    def get_queryset(self):
        return Article.objects.all().order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.is_ajax():
            html = render_to_string(
                "articles/_article_list.html",  # Assuming you have a template fragment for articles
                context,
                request=self.request,
            )
            return JsonResponse({"html": html})
        return super().render_to_response(context, **response_kwargs)


logger = logging.getLogger(__name__)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/article.html"
    context_object_name = "article"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        logger.info(f"ArticleDetailView context: {context}")
        logger.warning(f"ArticleDetailView author: {self.object.author}")
        context["author"] = self.object.author
        context["num_favorites"] = self.object.favorites.count()
        context["is_favorite"] = self.object.favorites.filter(
            pk=self.request.user.pk
        ).exists()
        context["comments"] = (
            Comment.objects.filter(article=self.object)
            .select_related("author")
            .order_by("-created")
        )

        logger.info(f"# get_context_data: {context}")

        context["comment_form"] = CommentForm()
        return context
