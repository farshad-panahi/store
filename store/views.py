from django.shortcuts import render

from .models import Product, Customer, OrderItem, Order, Comment
from django.db.models import Count, Sum
def show_data(request):
	co = Customer.objects.annotate(customer_order=Count('orders'))

	context = {
		'co': co
	}
	return render(
		request, 'store/store.html', context=context)

