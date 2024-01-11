from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingCartViewSet, TagsViewSet,
                    UserSubscriptionViewSet, UserSubscribeView)

router = DefaultRouter()

router.register(r'tags', TagsViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'recipes/(?P<recipe_id>\d+)/favorite', FavoriteViewSet,
                basename='favorite')
router.register(r'recipes/(?P<recipe_id>\d+)/shopping_cart',
                ShoppingCartViewSet, basename='shoppingcart')

urlpatterns = [
    path('users/subscriptions/',
         UserSubscriptionViewSet.as_view({'get': 'list'})),
    path('users/<int:user_id>/subscribe/', UserSubscribeView.as_view()),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
