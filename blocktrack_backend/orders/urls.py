from django.urls import path
from .views import CreateOrderView, ReadOrderView

urlpatterns = [
    path("create-order/", CreateOrderView.as_view()),
    path('read-order/<str:order_id>/', ReadOrderView.as_view()),
]
