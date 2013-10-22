from django.core.paginator import Paginator, EmptyPage
from django.conf import settings


def get_page_no(payload):
    """Determines the page number from the payload."""
    page_no = payload.get('page', 1)
    try:
        page_no = int(page_no)
    except ValueError:
        page_no = 1
    if page_no < 1:
        page_no = 1
    return page_no


def get_page(object_list, page_no):
    """Returns a ``Paginator`` page with the given details."""
    paginator = Paginator(object_list, settings.PAGINATOR_PAGE_SIZE)
    try:
        page = paginator.page(page_no)
    except EmptyPage:
        page = paginator.page(1)
    return page


def get_order_value(payload, field_list):
    """Validates the ``sort`` value in the payload.

    The value is validated from the list of params passed as a field_list.
    """
    sort_by = payload.get('order', None)
    reverse_list = ['-%s' % f for f in field_list]
    final_list = field_list + reverse_list
    return sort_by if sort_by in final_list else None
