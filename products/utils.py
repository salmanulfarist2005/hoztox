from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


def GetResponse(message='', error=False, status=200):
    """
    Standard API Response Format
    {
        "error": false,
        "message": ...
    }
    """
    return Response({'error': error, 'message': message}, status=status)



class StandardPagination(PageNumberPagination):
    page_size = 10                          
    page_size_query_param = 'page_size'      
    max_page_size = 100                      



def get_paginated_response(
    request,
    queryset,
    serializer_class,
    pagination_class=StandardPagination,
    many=True,
    context=None
):
    """
    Apply pagination to ANY queryset + serializer.
    This avoids writing pagination code in each view.
    """

    paginator = pagination_class()
    page = paginator.paginate_queryset(queryset, request)

    serializer_context = {"request": request}
    if context:
        serializer_context.update(context)

    if page is not None:
        serializer = serializer_class(page, many=many, context=serializer_context)
        paginated_data = paginator.get_paginated_response(serializer.data).data
        return GetResponse(message=paginated_data)

    serializer = serializer_class(queryset, many=many, context=serializer_context)
    return GetResponse(message=serializer.data)




def apply_search(queryset, search_value, *fields):
    """
    Apply search across multiple fields.
    Usage:
        queryset = apply_search(queryset, search, 'name', 'email')
    """
    from django.db.models import Q

    if search_value:
        q = Q()
        for f in fields:
            q |= Q(**{f"{f}__icontains": search_value})
        queryset = queryset.filter(q)

    return queryset