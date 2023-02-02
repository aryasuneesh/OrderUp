from django.shortcuts import render
from django.http import JsonResponse
import datetime
import json
from .models import  *
from .utils import *
import uuid


# remember to change the code here, to show total cart value at about page too
def about(request):
    data  = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems}
    return render(request, 'store/about.html', context)

def store(request):
    data  = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    data  = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data  = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items':items, 'order':order, 'cartItems':cartItems, 'shipping':False}
    return render(request, 'store/checkout.html', context)





def status(request):
    orderno = Order.objects.all().order_by('-orderstatus')
    data  = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products":products, 'cartItems':cartItems, 'orderno':orderno}
    return render(request, 'store/status.html', context)




def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action :', action)
    print('productId :',productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    # Adding or removing the quantity of the product in the cart.
    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)

    else:
        # guestOrder function is present in utils.py
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    

    if total == order.get_cart_total:
        order.complete = True
    order.transaction_id = str(uuid.uuid4())[:5]
    order.save()

    # if order.shipping == True:
    #     ShippingAddress.objects.create(
    #         customer = customer,
    #         order = order,
    #         address = data['shipping']['address'],
    #         city = data['shipping']['city'],
    #         state = data['shipping']['state'],
    #         zipcode = data['shipping']['zipcode'],
    #         )






    return JsonResponse("Payment submitted...",safe=False)
