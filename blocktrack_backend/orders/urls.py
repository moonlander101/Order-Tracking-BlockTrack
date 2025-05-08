from django.urls import path
from .views import CreateOrderView, OrderByWarehouse, ReadOrderView, OrderListCreateView, OrderDetailView

urlpatterns = [
    path("create-order/", CreateOrderView.as_view()),
    path('read-order/<str:order_id>/', ReadOrderView.as_view()),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<str:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/warehouse/<int:warehouse_id>', OrderByWarehouse.as_view(), name='order-detail-by-warehouse')
    # path("api/legacy/order/<str:order_id>/", ReadOrderLegacyView.as_view()),
]
