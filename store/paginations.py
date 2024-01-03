from rest_framework.pagination import PageNumberPagination


class DefaultPageination(PageNumberPagination):
	page_size = 10
