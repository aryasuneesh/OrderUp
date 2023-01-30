import json
from .models import *

def cookieCart(request):
    """
    It takes the request object and returns a dictionary with the cartItems, order, and items.
    
    :param request: The request object
    :return: A dictionary with the following keys:
    cartItems: The total number of items in the cart
    order: A dictionary with the following keys:
    get_cart_total: The total cost of all items in the cart
    get_cart_items: The total number of items in the cart
    shipping: A boolean that is True if the cart contains any non-digital items
    items
    """
    try:
        cart = json.loads(request.COOKIES['cart'])
    except :
        cart = {}

    print('Cart: ',cart)
    items = []
    order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total']+=total
            order['get_cart_items']+=cart[i]['quantity']

            item = {
                'product':{
                    'id':product.id,
                    'name':product.name,
                    'price':product.price,
                    'imageURL':product.imageURL
                    },
                'quantity':cart[i]['quantity'],
                'get_total':total,
                }
            items.append(item)

            if product.digital == False:
                order['shipping'] = True
        except:
            pass
    return {'cartItems':cartItems, 'order':order, 'items':items}


def cartData(request):
    """
    If the user is authenticated, get the customer, order, and items. If not, get the cookie data
    
    :param request: The request object
    :return: A dictionary with the keys 'cartItems', 'order', and 'items'
    """
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems':cartItems, 'order':order, 'items':items}


def guestOrder(request, data):
    print("User is not logged in..")

    print("COOKIES:", request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created  = Customer.objects.get_or_create(
        email = email,
        )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
        )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])
        orderItem = OrderItem.objects.create(
            product = product,
            order = order,
            quantity = item['quantity']
            )
    return customer, order
