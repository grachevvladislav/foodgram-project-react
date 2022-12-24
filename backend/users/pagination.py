from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    #page_size_query_param = 'limit'
    limit_query_param = 'limit'
    offset_query_param = 'page'
