from collections import OrderedDict

from rest_framework.pagination import CursorPagination as _CursorPagination
from rest_framework.pagination import LimitOffsetPagination as _LimitOffsetPagination

from {{cookiecutter.project_slug}}.common.http import api_response


def get_paginated_response(*, pagination_class, serializer_class, queryset, request, view):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True)

    return api_response(data=serializer.data)


def get_paginated_response_context(*, pagination_class, serializer_class, queryset, request, view):
    paginator = pagination_class()

    page = paginator.paginate_queryset(queryset, request, view=view)

    if page is not None:
        serializer = serializer_class(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    serializer = serializer_class(queryset, many=True, context={"request": request})

    return api_response(data=serializer.data)


class LimitOffsetPagination(_LimitOffsetPagination):
    default_limit = 10
    max_limit = 50

    def get_paginated_data(self, data):
        return OrderedDict(
            [
                ("limit", self.limit),
                ("offset", self.offset),
                ("count", self.count),
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )

    def get_paginated_response(self, data):
        """
        We redefine this method in order to return `limit` and `offset`.
        This is used by the frontend to construct the pagination itself.
        """
        return api_response(
            data=OrderedDict(
                [
                    ("limit", self.limit),
                    ("offset", self.offset),
                    ("count", self.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )


class CursorPagination(_CursorPagination):
    """
    Stable pagination for large / frequently changing lists.

    Prefer this over limit/offset when rows are inserted/deleted while clients page
    (feeds, event logs, high-churn tables). Clients follow `next` / `previous` cursors.
    """

    page_size = 10
    max_page_size = 50
    page_size_query_param = "page_size"
    ordering = "-created_at"

    def get_paginated_response(self, data):
        return api_response(
            data=OrderedDict(
                [
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
