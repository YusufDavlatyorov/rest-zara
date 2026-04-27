from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import RegisterUserSerializer, MeSerializer
from .permissions import IsAdminRole
# --- ПУБЛИЧНЫЕ ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterUserSerializer
    permission_classes = [permissions.AllowAny]

# --- ДЛЯ АВТОРИЗОВАННЫХ (ME) ---

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

# --- ТОЛЬКО ДЛЯ АДМИНОВ (USERS) ---

class UserListView(generics.ListAPIView):
    queryset = User.objects.all().select_related('profile')
    serializer_class = MeSerializer
    permission_classes = [IsAdminRole] # Только Admin

class UserDetailAdminView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all().select_related('profile')
    serializer_class = MeSerializer
    permission_classes = [IsAdminRole] # Только Admin
