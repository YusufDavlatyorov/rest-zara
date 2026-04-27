from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import ChatSerializer
from .services import ZaraStylistService

class ZaraChatAPIView(APIView):
    serializer_class = ChatSerializer 

    @swagger_auto_schema(
        manual_parameters=[
            # Оставляем ТОЛЬКО ОДНО поле в Swagger
            openapi.Parameter(
                'vopros', 
                openapi.IN_FORM, 
                type=openapi.TYPE_STRING, 
                description="Введите ваш вопрос", 
                required=True
            ),
        ],
        consumes=['application/x-www-form-urlencoded', 'multipart/form-data']
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            vopros = serializer.validated_data.get('vopros')
            
            # session_id делаем скрытым (например, 'default' или берем из сессии)
            session_id = "user_session_1" 
            
            stylist = ZaraStylistService()
            try:
                # Передаем текст вопроса в сервис
                answer = stylist.get_response(session_id, vopros)
                return Response({"answer": answer})
            except Exception as e:
                return Response({"error": str(e)}, status=500)
        
        return Response(serializer.errors, status=400)
