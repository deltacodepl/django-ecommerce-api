from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, views, status
from rest_framework.response import Response
import stripe

from payment.models import Payment
from payment.serializers import PaymentSerializer
from orders.models import Order


stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        res = super().get_queryset()
        user_id = self.kwargs.get('user_id')
        return res.filter(order__buyer=user_id)


class StripeCheckoutSessionCreateAPIView(views.APIView):
    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get('order_id'))

        order_items = []

        for order_item in order.order_items.all():
            product = order_item.product
            quantity = order_item.quantity

            data = {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount_decimal': product.price,
                    'product_data': {
                        'name': product.name,
                        'description': product.desc,
                        'images': [f'{settings.BACKEND_DOMAIN}{product.image.url}']
                    }
                },
                'quantity': quantity
            }

            order_items.append(data)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=order_items,
            mode='payment',
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL
        )

        payment = get_object_or_404(Payment, order=self.kwargs.get('order_id'))
        payment.status = 'C'
        payment.save()

        order.status = 'C'
        order.save()

        return Response({'sessionId': checkout_session['id']}, status=status.HTTP_201_CREATED)
