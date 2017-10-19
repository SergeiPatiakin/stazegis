"""stazegis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

from mainapp.views import HomeView, ArticleSpatialQueryView, ArticleAPIView, ArticleCreateView, UserRegisterView

urlpatterns = [
    url(r'^$', RedirectView.as_view(pattern_name="home-view")),
    url(r'^view/', HomeView.as_view(), name="home-view"),
    url(r'^tracks/([0-9a-z_\-]+)/', ArticleAPIView.as_view()),
    url(r'^trackquery/', ArticleSpatialQueryView.as_view()),
    url(r'^login/$', auth_views.login, {'template_name': 'mainapp/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
    url(r'^register/$', UserRegisterView.as_view()),
    url(r'^createarticle/$', ArticleCreateView.as_view()),
    url(r'^draceditor/', include('draceditor.urls')),
    url(r'^admin/', admin.site.urls),
]
