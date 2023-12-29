from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.constraints import (
    UniqueConstraint
)

User = get_user_model()


class Tags(models.Model):
    # Модель тега
    name = models.CharField(
        'Название',
        max_length=56,
        unique=True,
    )
    color = models.CharField(
        'Цвет',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг',
        max_length=56,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredients(models.Model):
    # Модель ингредиента
    name = models.CharField(
        'Название',
        max_length=56,
        unique=True,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=56,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    # Модель рецепта, связь с ингредиентами идет через связь многие ко многим
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=225,
    )
    image = models.ImageField(
        'Изображение',
        upload_to='media/',
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='RecipeIngredients',
        through_fields=('recipe', 'ingredient'),
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tags,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
    )
    text = models.TextField(
        'Текст',
    )
    is_favorited = models.BooleanField(
        'В избранном',
        default=False,
    )
    is_in_shopping_cart = models.BooleanField(
        'В корзине',
        default=False,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):
    # Промежуточная таблица, связывающая рецепты и ингредиенты
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент из рецепта'
        verbose_name_plural = 'Ингредиенты из рецепта'
        constraints = [
            UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredients'
            )
        ]


class Shoppingcart(models.Model):
    # Модель корзины
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingrecipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingrecipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в корзину.'


class Favorite(models.Model):
    # Модель избранных рецептов
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriterecipe',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favoriterecipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное.'
