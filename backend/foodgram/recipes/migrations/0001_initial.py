# Generated by Django 3.2 on 2023-12-28 00:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранные',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=56, unique=True, verbose_name='Название')),
                ('measurement_unit', models.CharField(max_length=56, verbose_name='Единица измерения')),
            ],
            options={
                'verbose_name': 'Ингредиент',
                'verbose_name_plural': 'Ингредиенты',
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=225, verbose_name='Название')),
                ('image', models.ImageField(blank=True, upload_to='foodgram/images/', verbose_name='Изображение')),
                ('cooking_time', models.PositiveSmallIntegerField(verbose_name='Время приготовления')),
                ('text', models.TextField(verbose_name='Текст')),
                ('is_favorited', models.BooleanField(default=False, verbose_name='В избранном')),
                ('is_in_shopping_cart', models.BooleanField(default=False, verbose_name='В корзине')),
            ],
            options={
                'verbose_name': 'Рецепт',
                'verbose_name_plural': 'Рецепты',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Ингредиент из рецепта',
                'verbose_name_plural': 'Ингредиенты из рецепта',
            },
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=56, unique=True, verbose_name='Название')),
                ('color', models.CharField(max_length=7, unique=True, verbose_name='Цвет')),
                ('slug', models.SlugField(max_length=56, unique=True, verbose_name='Слаг')),
            ],
            options={
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.CreateModel(
            name='Shoppingcart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingrecipe', to='recipes.recipe')),
            ],
            options={
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины',
                'ordering': ['-id'],
            },
        ),
    ]