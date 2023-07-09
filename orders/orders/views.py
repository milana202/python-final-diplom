from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework import status
# from rest_framework.views import APIView
from .models import User
from .serializers import UserRegistrSerializer


# Создаём класс для регистрации пользователей
class RegistrUserView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrSerializer
    permission_classes = [AllowAny]

    # Создаём метод для создания нового пользователя
    def post(self, request, *args, **kwargs):
        serializer = UserRegistrSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            serializer.save()
            data['response'] = True
            return Response(data, status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data)


# class ModelnameViewSet(ModelViewSet):
#     queryset = Modelname.objects.all()
#     serializer_class = ModelnameSerializer
#     filterset_fields = ['список полей пото которым можно выполнять фильтрацию']


#     def list(self, request):
#         # постотреть все объекты
#         return Response()
#
#     def retrieve(self,request):
# #         посмотреть один объект
#         return Response()
#
#     def destroy(self,request):
# #         удвление объекта
#         return Response()
#
#     def update(self,request):
# #         обновление
#         return Response()
#
#    def create(self,request):
# #         создание
#         return Response()


# class SomethingView(APIView):
#     def get(self, request):
#         return Response()
#
#     def post(self, request):
#         return Response({'status': 'ok'})

# class SomethingView(ListAPIView):
#     queryset = Modelname.objects.all()
#     serializer_class = ModelnameSerializer

# зарегистрировать в урл: урл - вью-функция