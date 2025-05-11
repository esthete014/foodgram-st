"""
URL configuration for foodgram_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

# Django core imports
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# Third-party imports
from rest_framework.routers import DefaultRouter

# Local application imports
from recipes.views import IngredientViewSet, RecipeViewSet, recipe_short_link_redirect
from users.views import UserAvatarView, UserViewSet

api_router_v1 = DefaultRouter()
api_router_v1.register(r"recipes", RecipeViewSet)
api_router_v1.register(r"ingredients", IngredientViewSet)
api_router_v1.register(r"users", UserViewSet, basename="users")

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "s/<int:recipe_id>/",
        recipe_short_link_redirect,
        name="recipe_short_link_redirect",
    ),
    path("api/users/me/avatar/", UserAvatarView.as_view(), name="user-me-avatar"),
    path("api/auth/", include("djoser.urls.authtoken")),
    path("api/", include(api_router_v1.urls)),
]

if settings.DEBUG:
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            path("__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
