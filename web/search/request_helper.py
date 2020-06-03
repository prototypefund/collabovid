import requests
from django.conf import settings
import logging
from data.models import Paper
from django.core.paginator import Paginator
from search.paginator import ScoreSortPaginator

import json


class SearchRequestHelper:

    def __init__(self, start_date, end_date, search_query, authors, authors_connection, journals, categories,
                 score_min=0.6):
        logger = logging.getLogger(__name__)

        self._response = None
        self._error = False

        try:
            response = requests.get(settings.SEARCH_SERVICE_URL, params={
                'start_date': start_date,
                'end_date': end_date,
                'search': search_query,
                'score_min': score_min,
                'authors': authors,
                'authors_connection': authors_connection,
                'categories': categories,
                'journals': journals
            })
            response.raise_for_status()

            self._response = response.json()
        except requests.exceptions.Timeout:
            logger.error("Search Request Connection Timeout")
            self._error = True
        except requests.exceptions.HTTPError:
            self._error = True
        except requests.exceptions.RequestException as e:
            logger.error("Some unknown request exception occured", e)
            self._error = True

        if self._response is None:
            self._error = True
        else:
            self._papers = Paper.objects.filter(pk__in=self._response.keys())

    @property
    def error(self):
        return self._error

    @property
    def papers(self):
        return self._papers

    def paginator_ordered_by(self, criterion, page_count=10):

        if criterion == Paper.SORTED_BY_TOPIC_SCORE:
            paginator = Paginator(self.papers.order_by("-topic_score", "-published_at"), page_count)
        elif criterion == Paper.SORTED_BY_NEWEST:
            paginator = Paginator(self.papers.order_by("-published_at"), page_count)
        elif criterion == Paper.SORTED_BY_SCORE:
            filtered_items = []
            for doi in self.papers.order_by("-published_at").values_list('doi', flat=True):
                filtered_items.append((doi, self._response[doi]))

            paper_score_items = sorted(filtered_items, key=lambda x: x[1], reverse=True)

            paginator = ScoreSortPaginator(paper_score_items, page_count)
        else:
            paginator = Paginator(self.papers, page_count)
            logger = logging.getLogger(__name__)
            logger.warning("Unknown sorted by" + criterion)
        return paginator
