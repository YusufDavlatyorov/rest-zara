from django.urls import path
from .views import ZaraChatAPIView

urlpatterns = [
    # Эндпоинт будет доступен по адресу /api/ai/chat/
    path('chat/', ZaraChatAPIView.as_view(), name='zara-ai-chat'),
]
