from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout



def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def product(request, pk):
	product = Product.objects.get(id=pk)
	data = cartData(request)
	cartItems = data['cartItems']
	context = {
		"product": product,
		'cartItems': cartItems
	}
	return render(request, "store/product.html", context)


def login(request):
	pass


def signup(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		name = request.POST.get('name')
		pass1 = request.POST.get('pass1')
		pass2 = request.POST.get('pass2')

		if pass1 == pass2:
			user = User.objects.create_user(username=username, email=email, password=pass1)
			user.save()
			customer = Customer.objects.create(user=user, name=name, email=email)
			customer.save()
			login(request, user)
			messages.success(request, 'Account created successfully')
			return redirect("store")
		else:
			messages.success(request, 'Something went wrong')
			return redirect("register")

	context = {'cartItems':cartItems}
	
	return render(request, 'store/register.html', context) 



def loginUser(request):
	if request.method == "POST":
		username = request.POST.get('username')
		password = request.POST.get('pass1')
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, "Login successful")
			return redirect('store')
		else:
			messages.success(request, "Wrong credentials")
			return redirect("login")
	
	else:
		return render(request, "store/login.html")
	

def logoutUser(request):
	logout(request.user)
	messages.success(request, "Logged out successfully")
	return redirect("store")