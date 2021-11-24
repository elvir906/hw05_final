from django.core.paginator import Paginator
from django.conf import settings


def page_obj_gen(request, posts):
    paginator = Paginator(posts, settings.POST_COUNT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
