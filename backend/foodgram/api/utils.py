import base64

from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    """Функция для работы с изображениями."""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


def create_model_instance(request, instance, serializer_name):
    """Вспомогательная функция для добавления
    рецепта в избранное либо список покупок.
    """
    serializer = serializer_name(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_model_instance(request, model_name, instance, error_message):
    """Вспомогательная функция для удаления рецепта
    из избранного либо из списка покупок.
    """
    if not model_name.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)
    model_name.objects.filter(user=request.user, recipe=instance).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
