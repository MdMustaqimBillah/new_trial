# Payment/urls.py
from django.urls import path
from .views import CreateStripeCheckoutSession, stripe_webhook

urlpatterns = [
    # Create Stripe Checkout Session for a specific order
    path('stripe/create-checkout/<int:order_id>/', 
         CreateStripeCheckoutSession.as_view(), name='stripe-checkout'),

    # Stripe Webhook endpoint (called by Stripe automatically)
    path('stripe/webhook/', stripe_webhook, name='stripe-webhook'),
]
