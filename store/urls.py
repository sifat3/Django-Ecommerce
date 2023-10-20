from django.urls import path

from . import views

urlpatterns = [
	#Leave as empty string for base url
	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),
	path('product/<int:pk>', views.product, name="product"),
    path('register/', views.signup, name="register"),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logoutUser, name='logout'),

]