from groq import Groq
from django.conf import settings
from .models import ChatHistory

class ZaraStylistService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        # Главная инструкция для ИИ
        self.system_prompt = (
            "Ты — эксперт-стилист магазина Zara. Твоя задача — помогать подбирать одежду. "
            "1. Отвечай ТОЛЬКО на вопросы о товарах и стиле. На другие темы вежливо отказывай. "
            "2. Если клиент хочет совета, обязательно спроси его: рост, вес, телосложение и возраст. "
            "3. Понимай русский язык, даже если он написан английскими буквами (транслит). "
            "4. Будь вежливым и профессиональным."
        )

    def get_response(self, session_id, user_text):
        # 1. Загружаем историю из БД
        history = ChatHistory.objects.filter(session_id=session_id).order_by('created_at')
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for msg in history:
            messages.append({"role": msg.role, "content": msg.content})
        
        messages.append({"role": "user", "content": user_text})

        # 2. Запрос к Groq
        completion = self.client.chat.completions.create(
            # Использована актуальная модель, доступная в Groq
            model="llama-3.3-70b-versatile", 
            messages=messages,
        )
        # Правильное обращение к контенту ответа
        ai_answer = completion.choices[0].message.content

        # 3. Сохраняем переписку в базу
        ChatHistory.objects.create(session_id=session_id, role="user", content=user_text)
        ChatHistory.objects.create(session_id=session_id, role="assistant", content=ai_answer)

        return ai_answer
