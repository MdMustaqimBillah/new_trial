# Payment/views.py
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from Order.models import Order
from Cart.models import Cart
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY

# ----------------------------
# Create Stripe Checkout Session
# ----------------------------
class CreateStripeCheckoutSession(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            # Get the order that needs payment
            order = Order.objects.get(id=order_id, user=request.user, purchased=False)
        except Order.DoesNotExist:
            return Response({"error": "Order not found or already purchased."}, status=status.HTTP_404_NOT_FOUND)

        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': f"Order {order.order_id}"},
                        'unit_amount': int(order.total * 100),  # amount in cents
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:8000/payment-success/?session_id={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:8000/payment-cancel/',
            )

            # Store Stripe payment intent ID in order
            order.stripe_payment_intent = checkout_session.payment_intent
            order.save()

            return Response({"checkout_session_id": checkout_session.id})

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ----------------------------
# Stripe Webhook
# ----------------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'whsec_...'  # Your Stripe webhook secret

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception as e:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_intent = session['payment_intent']

        try:
            # Find the order
            order = Order.objects.get(stripe_payment_intent=payment_intent)

            # Create Payment object
            Payment.objects.create(
                user=order.user,
                order_item=order,
                address=order.user.address,
                city=order.user.city,
                division=order.user.division,
                country=order.user.country,
                zip_code=order.user.zip_code,
                payment_id=payment_intent
            )

            # Mark order as purchased
            order.purchased = True
            order.save()

        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)
