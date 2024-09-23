from django.urls import path
from .views import IndexView, ChatView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('chat/', ChatView.as_view(), name='chat'),
]