from django.core.paginator import Paginator


POSTS_NUMBER: int = 10


def paginat(request, post):
    paginator = Paginator(post, POSTS_NUMBER)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
