from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

# class DefaultPagination(PageNumberPagination):
#     page_size = 30

class DefaultPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'current_page': self.get_page_number(self.request, paginator=PageNumberPagination),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })