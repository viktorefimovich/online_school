from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Стандартный пагинатор для вывода курсов и уроков.
    """
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 20
