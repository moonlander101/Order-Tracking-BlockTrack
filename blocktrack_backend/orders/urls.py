from django.urls import path
from .views import CreateOrderView, OrderByWarehouse, ReadOrderView, OrderListCreateView, OrderDetailView, OrderStatusUpdateView, UserOrderListView

urlpatterns = [
    path("create-order/", CreateOrderView.as_view()),
    path('read-order/<str:order_id>/', ReadOrderView.as_view()),
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/vendor/<int:user_id>/', UserOrderListView.as_view(), name='order-by-user'),
    path('orders/warehouse/<int:warehouse_id>', OrderByWarehouse.as_view(), name='order-detail-by-warehouse'),
    path('orders/<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='status-update')
    # path("api/legacy/order/<str:order_id>/", ReadOrderLegacyView.as_view()),
]
