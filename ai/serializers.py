from rest_framework import serializers

class ChatSerializer(serializers.Serializer):
    # Оставляем только поле для вопроса
    vopros = serializers.CharField(required=True, help_text="Напишите ваш вопрос здесь")
