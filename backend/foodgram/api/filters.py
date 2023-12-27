from django_filters.rest_framework.filters import (
    FilterSet,
    BooleanFilter,
    ModelMultipleChoiceFilter,
    CharFilter
)

from recipes.models import (
    Ingredient,
    Recipe,
    Tags,
)


class RecipeFilter(FilterSet):
    # Фильтр для рецептов
    tags = ModelMultipleChoiceFilter(
        queryset=Tags.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = BooleanFilter(
        method='get_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            return queryset.filter(carts__user=self.request.user)
        return queryset


class IngredientFilter(FilterSet):
    # Фильтр для ингредиентов
    name = CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
