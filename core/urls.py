"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers, permissions
from rest_framework.documentation import include_docs_urls

from blogging import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'activity', views.PostInteractionViewSet)

schema_view = get_schema_view(
    openapi.Info(
        #  add your swagger doc title
        title="Blogging API",
        #  version of the swagger doc
        default_version='v1',
        # first line that appears on the top of the doc
        description="example blogging models and API functionality",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="div.agicha@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('api/', include(router.urls)),
    # path('api/timeline/<int:pk>/', views.TimelineView.as_view()),
    path('api/timeline/', views.TimelineView.as_view(), name='retrieve_user_timeline'),
    path('api/follow/', views.FollowUserView.as_view(), name='follow_user'),
    path('admin/', admin.site.urls),
    path('docs/', include_docs_urls(title='Blogging API', public=False)),
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui'),
    re_path('^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
