from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
# Заменить на кастомную модель


class Tag(models.Model):

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


class Ingredient(models.Model):

    name = models.CharField(
        'Название',
        max_length=56,
        unique=True,
    )
    measurement = models.CharField(
        'Единица измерения',
        max_length=56,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):

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
        upload_to='recipes/',
        blank=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    time_to_cook = models.PositiveIntegerField(
        'Время приготовления',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент',
    )
    amount = models.PositiveIntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент из рецепта'
        verbose_name_plural = 'Ингредиенты из рецепта'