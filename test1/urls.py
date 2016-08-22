"""test1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.conf import settings
from django.conf.urls.static import static

import test1.core.views as views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^contactus/', views.contactus),
    url(r'^history/(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d+)/$', views.history),
    url(r'^history/$', views.history_default),
    url(r'^inbound/$', views.handle_inbound),
    url(r'^login/$', auth_views.login),
    url(r'^register/$', views.register),
    url(r'^remove/$', views.remove),
    url(r'^outbox/$', views.outbound_message),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)