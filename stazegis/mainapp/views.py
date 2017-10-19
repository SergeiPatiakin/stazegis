from django.shortcuts import render
from django.views.generic.base import View
from django.db import connection, IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Article, User
from .serializers import ArticleSerializer
from .forms import UserRegisterForm, ArticleForm

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'mainapp/index.html', {})

class ArticleAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk):
        try:
            article = Article.objects.get(pk=pk)
        except Article.DoesNotExist:
            return Response({"error": "Article does not exist"}, status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response({"error": "Malformed UUID for Article"}, status.HTTP_400_BAD_REQUEST)
        if not article.is_visible:
            return Response(status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

class ArticleSpatialQueryView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        sql_parameters = {}
        try:
            bbox = request.GET["bbox"].split(",")
            sql_parameters["min_x"] = bbox[0]
            sql_parameters["min_y"] = bbox[1]
            sql_parameters["max_x"] = bbox[2]
            sql_parameters["max_y"] = bbox[3]
        except KeyError:
            return Response({"error": "Bad or missing bbox"}, status.HTTP_400_BAD_REQUEST)

        try:
            layer_code = request.GET["layer_code"]
        except KeyError:
            return Response({"error": "Missing layer_code"}, status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            if layer_code=="ALL":
                extra_predicate = ""
            elif layer_code=="PED" or layer_code=="CYC":
                extra_predicate = " AND track_type=%(track_type)s"
                sql_parameters["track_type"] = layer_code
            else:
                return Response({"error": "Bad layer code"}, status.HTTP_400_BAD_REQUEST)

            sql = ("SELECT id FROM mainapp_article WHERE ST_Intersects(geom, ST_MakeEnvelope(%(min_x)s, %(min_y)s, "
                  "%(max_x)s, %(max_y)s, 4326))"+extra_predicate)

            cursor.execute(sql, sql_parameters)
            rows = cursor.fetchall()
            response_json = [str(r[0]) for r in rows]
            return Response(response_json)

class UserRegisterView(View):
    def get(self, request, *args, **kwargs):
        form = UserRegisterForm()
        context = {
            'form': form,
        }
        return TemplateResponse(request, 'mainapp/register.html', context)

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(data=request.POST)
        if form.is_valid():
            try:
                user = User.objects.create_user(
                    email=form.cleaned_data['email'],
                    name=form.cleaned_data['first_name'],
                    password=form.cleaned_data['password']
                )

                messages.success(request, 'User registration successful')
                # Clear form fields
                form = UserRegisterForm()
            except IntegrityError as e:
                messages.error(request, 'An account with this email address already exists.')
        context = {
            'form': form,
        }
        return TemplateResponse(request, 'mainapp/register.html', context)

class ArticleCreateView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        form = ArticleForm()
        context = {
            'form': form,
        }
        return TemplateResponse(request, 'mainapp/createarticle.html', context)


    def post(self, request, *args, **kwargs):
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Track submission successful. The track will appear on the site once approved by an administrator.')
            # Clear form fields
            form = ArticleForm()
        context = {
            'form': form,
        }
        return TemplateResponse(request, 'mainapp/createarticle.html', context)