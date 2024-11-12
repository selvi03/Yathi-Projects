from django.urls import path

from . import views

app_name = 'DjangoHUDApp'
urlpatterns = [
    path('', views.index, name='index'),
    path('404/', views.error404, name='error404')
]