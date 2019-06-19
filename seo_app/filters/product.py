from rest_framework.filters import BaseFilterBackend


class ProductFilter(BaseFilterBackend):
    """product列表过滤"""

    filter_keys = {
        "name": "name__icontains",
    }

    def filter_queryset(self, request, queryset, view):
        filte_kwargs = {"user": request.user}
        for filter_key in self.filter_keys.keys():
            val = request.query_params.get(filter_key, '')
            if val is not '':
                filte_kwargs[self.filter_keys[filter_key]] = val
        if not filte_kwargs:
            return []
        queryset = queryset.filter(**filte_kwargs)
        return queryset
