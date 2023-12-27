from django.urls import (
    include,
    path
)
from rest_framework.routers import DefaultRouter

from .views import (
    TagsViewSet,
    IngredientViewSet,
    UserSubscriptionViewSet
)

router = DefaultRouter()

router.register(
    r'tags',
    TagsViewSet,
    basename='tags'
    )
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('users/subscriptions/',
         UserSubscriptionViewSet.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
