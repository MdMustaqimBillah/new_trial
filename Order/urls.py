from django.urls import path
from Order.views import CreateOrderView, DeleteOrderView,DownloadOrdersCSVView

urlpatterns = [
    path('order/', CreateOrderView.as_view(), name='create-order'),
    path('order/<int:order_id>/', DeleteOrderView.as_view(), name='delete-order'),
    path('orders/download-csv/', DownloadOrdersCSVView.as_view(), name='download-orders-csv')    
]
