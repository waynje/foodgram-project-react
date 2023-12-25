from django.db.models import (
    Model,
    CharField,
    TextField,
    SlugField,
    ForeignKey,
    ManyToManyField,
    ImageField,
    CASCADE,
    PositiveSmallIntegerField,
    BooleanField
)
from django.db.models.constraints import (
    UniqueConstraint
)
from django.contrib.auth import get_user_model

User = get_user_model()
# Заменить на кастомную модель


class Tags(Model):
    # Модель тега
    name = CharField(
        'Название',
        max_length=56,
        unique=True,
    )
    color = CharField(
        'Цвет',
        max_length=7,
        unique=True,
    )
    slug = SlugField(
        'Слаг',
        max_length=56,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(Model):
    # Модель ингредиента
    name = CharField(
        'Название',
        max_length=56,
        unique=True,
    )
    measurement_unit = CharField(
        'Единица измерения',
        max_length=56,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(Model):
    # Модель рецепта, связь с ингредиентами идет через связь многие ко многим
    author = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='recipes',
        verbose_name='Автор',
    )
    name = CharField(
        'Название',
        max_length=225,
    )
    image = ImageField(
        'Изображение',
        upload_to='foodgram/images/',
        blank=True,
    )
    ingredients = ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиенты',
    )
    tags = ManyToManyField(
        Tags,
        verbose_name='Теги',
    )
    cooking_time = PositiveSmallIntegerField(
        'Время приготовления',
    )
    text = TextField(
        'Текст',
    )
    is_favorited = BooleanField(
        'В избранном',
        default=False,
    )
    is_in_shopping_cart = BooleanField(
        'В корзине',
        default=False,
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self) -> str:
        return self.name


class RecipeIngredients(Model):
    # Промежуточная таблица, связывающая рецепты и ингредиенты
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт',
    )
    ingredient = ForeignKey(
        Ingredient,
        on_delete=CASCADE,
        related_name='recipeingredients',
        verbose_name='Ингредиент',
    )
    amount = PositiveSmallIntegerField(
        'Количество',
    )

    class Meta:
        verbose_name = 'Ингредиент из рецепта'
        verbose_name_plural = 'Ингредиенты из рецепта'
        constraints = [
            UniqueConstraint(
                fields=['ingredients', 'recipe'],
                name='unique_ingredients'
            )
        ]


class Shopping_cart(Model):
    # Модель корзины
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='shoppingrecipe',
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='shoppingrecipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в корзину.'


class Favorite(Model):
    # Модель избранных рецептов
    recipe = ForeignKey(
        Recipe,
        on_delete=CASCADE,
        related_name='favoriterecipe',
    )
    user = ForeignKey(
        User,
        on_delete=CASCADE,
        related_name='favoriterecipe',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'

    def __str__(self):
        return f'{self.user.username} добавил {self.recipe.name} в избраннное.'
