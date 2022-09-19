from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payment.views import PaymentViewSet, StripeCheckoutSessionCreateAPIView


app_name = 'payment'

router = DefaultRouter()
router.register(r'', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-checkout-session/<int:order_id>/',
         StripeCheckoutSessionCreateAPIView.as_view(), name='checkout_session')
]
