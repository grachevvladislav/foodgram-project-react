from rest_framework.pagination import LimitOffsetPagination


class CustomPagination(LimitOffsetPagination):
    limit_query_param = 'limit'
    offset_query_param = 'page'
