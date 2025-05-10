from django.urls import path
from .views import (
    SupplierRequestListCreate,
    SupplierRequestByWarehouse,
    SupplierRequestStatusUpdate,
    SupplierRequestGetOrPartialUpdate,
    SupplierRequestBySupplier,
    SupplierRequestMetrics,
    SupplierRequestWithNames
)

urlpatterns = [
    path('supplier-request/', SupplierRequestListCreate.as_view()),
    # path('supplier-request/warehouse/<int:warehouse_id>/', SupplierRequestByWarehouse.as_view()),
    path('supplier-request/<int:request_id>/status/', SupplierRequestStatusUpdate.as_view()),
    path('supplier-request/request/<int:request_id>/', SupplierRequestGetOrPartialUpdate.as_view()),
    path('supplier-request/supplier/<int:supplier_id>/', SupplierRequestBySupplier.as_view()),
    path('supplier-request/metrics/<int:supplier_id>/', SupplierRequestMetrics.as_view()),
    path('supplier-request/warehouse/<int:warehouse_id>/', SupplierRequestWithNames.as_view())
]