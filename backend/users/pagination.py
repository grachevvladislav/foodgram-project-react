from rest_framework.pagination import PageNumberPagination


class QueryParamPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'recipes_limit'
