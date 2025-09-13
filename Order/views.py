from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from Order.models import Order
from Cart.models import Cart
from Order.serializers import OrderSerializer
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

import csv


class CreateOrderView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # Get all un-ordered carts for the user
        carts = Cart.objects.filter(user=user, ordered=False)
        if not carts.exists():
            return Response({"detail": "No items in cart to order."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(user=user, purchased=False)

        # Add carts to order
        order.carts.set(carts)

        # Mark carts as ordered
        carts.update(ordered=True)

        # Calculate total
        total = sum(cart.total for cart in carts)
        order.total = total
        order.save()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class DeleteOrderView(APIView):
    permission_classes = [permissions.IsAdminUser]  # Only admin can delete

    def delete(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Reset carts' ordered status
        order.carts.update(ordered=False)

        # Delete the order
        order.delete()
        return Response({"detail": "Order deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class DownloadOrdersCSVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user, purchased=True)

        if not orders.exists():
            return Response({"detail": "No purchased orders found."}, status=404)

        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="my_orders.csv"'

        writer = csv.writer(response)
        # Write CSV header
        writer.writerow(['Order ID', 'Total', 'Created At', 'Cart Items'])

        for order in orders:
            # List all products in the order
            items = ', '.join([f"{cart.product.name} x {cart.quantity}" for cart in order.carts.all()])
            writer.writerow([order.order_id, order.total, order.created_at, items])

        return response

