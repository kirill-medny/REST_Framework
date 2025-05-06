from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    page_size = 5  # Количество элементов на странице
    page_size_query_param = "page_size"  # Разрешить клиенту изменять размер страницы
    max_page_size = 10  # Ограничьте максимальный размер страницы


class LessonPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 20
