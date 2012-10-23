# -*- coding: utf-8 -*-
from haystack.query import SearchQuerySet
from contrib.encodings import clean_accents

MAX_RESULTS = 10
DEFAULT_QUERY_TERM = "term"


def autocomplete(request, model=None, filters=None,
                 max_results=MAX_RESULTS, query_term=DEFAULT_QUERY_TERM):
    """
    autocomplete template.
    It intends to be used as a helper inside another view and not
    as a standalone view.

    *request* is a traditional GET request object send to a view
    *model* is the model to filter. If none, global SearchQuerySet is used
    *filters* is a list of filter strings to search for (inside *request.GET*)
    *max_results* is the maximum number of results to send. Defaults to 10
    *query_term* is the term string to get from the *request.GET* object and
        kickstart the search

    """
    q = request.GET.get(query_term)
    if not q:
        return []

    q = clean_accents(q)
    if model is not None:
        results = SearchQuerySet().models(model)
    else:
        results = SearchQuerySet()

    if not filters:
        filters = []
    for filter_field in filters:
        filter_q = request.GET.get(filter_field, None)
        if filter_q:
            results = results.filter(**{filter_field: filter_q})

    # Lazy Evaluation
    results = results.autocomplete(content_auto=q)[:max_results]
    results = [r.object for r in results if r.object]
    return results
