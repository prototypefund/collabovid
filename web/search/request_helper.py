from math import ceil

import requests
from django.conf import settings
import logging
from data.models import Paper, Author

from search.forms import SearchForm
from search.models import SearchQuery
from search.paginator import FakePaginator, ScoreSortPaginator
from search.tagify.tagify_searchable import AuthorSearchable
import json
from django.conf import settings
class SearchRequestHelper:

    def __init__(self, form: SearchForm, save_request: bool = False, highlight: bool = True):
        logger = logging.getLogger(__name__)

        self._response = None
        self._error = False
        self._form = form
        self._highlight = highlight

        try:
            response = requests.get(form.url, params={
                'form': form.to_json()
            })
            response.raise_for_status()

            self._response = response.json()
        except requests.exceptions.Timeout:
            logger.error("Search Request Connection Timeout")
            self._error = True
        except requests.exceptions.HTTPError:
            self._error = True
            logger.error("Http Error occured")
        except requests.exceptions.RequestException:
            logger.error("Some unknown request exception occured")
            self._error = True

        if self._response is None:
            self._error = True
        elif settings.SAVE_SEARCH_QUERIES and save_request and form.interesting:
            SearchQuery.objects.create(query=form.to_dict())

    @property
    def error(self):
        return self._error

    @property
    def response(self):
        return self._response

    def _parse_result_papers(self):
        result_dois = [p['doi'] for p in self.response['results']]
        papers = sorted(list(Paper.objects.filter(pk__in=result_dois).all()), key=lambda x: result_dois.index(x.doi))

        sorted_by = self._form.cleaned_data['sorted_by']
        for paper, infos in zip(papers, self.response['results']):
            if sorted_by in SearchForm.TRENDING_CHOICES.keys():
                if paper.altmetric_data and paper.altmetric_data.score > 0.0:
                    paper.trend = int(ceil(SearchForm.TRENDING_CHOICES[sorted_by]['value'](paper)))
                    paper.trend_description = SearchForm.TRENDING_CHOICES[sorted_by]['description']

            if self._highlight:
                if 'title' in infos:
                    paper.title = infos['title']
                if 'abstract' in infos:
                    paper.data.abstract = infos['abstract']
                if 'authors.full_name' in infos:
                    highlighted_full_names = infos['authors.full_name']

                    for highlighted_full_name in highlighted_full_names:
                        cleaned_full_name = highlighted_full_name.replace('<em>', '').replace('</em>', '')

                        for author in paper.highlighted_authors:
                            if author.full_name == cleaned_full_name:
                                author.display_name = highlighted_full_name

        paginator = FakePaginator(result_size=self.response['count'],
                                  page=self.response['page'],
                                  per_page=self.response['per_page'],
                                  papers=papers)

        authors = []
        for author in self.response['authors']:
            current_author = Author.objects.get(pk=author['pk'])
            current_author.display_name = author['full_name']
            current_author.json_object = json.dumps(AuthorSearchable.single_object(current_author))
            authors.append(current_author)

        return {'result_type': SearchForm.RESULT_TYPE_PAPERS,
                'paginator': paginator,
                'result_size': self.response['count'],
                'authors': authors}

    def _parse_result_statistics(self):
        result_dois = self.response['results']
        papers = Paper.objects.filter(pk__in=result_dois)
        return {'result_type': SearchForm.RESULT_TYPE_STATISTICS, 'papers': papers}

    def build_search_result(self):
        if not self.error:
            if self._form.cleaned_data['result_type'] == SearchForm.RESULT_TYPE_PAPERS:
                return self._parse_result_papers()
            elif self._form.cleaned_data['result_type'] == SearchForm.RESULT_TYPE_STATISTICS:
                return self._parse_result_statistics()

        raise ValueError("Search yielded no result or used an invalid result type")


class SimilarPaperRequestHelper:

    def __init__(self, dois, total_papers, papers_per_page=0):
        logger = logging.getLogger(__name__)

        self._response = None
        self._error = False
        self._papers = None
        self._papers_per_page = papers_per_page
        self._result_dois = None
        try:
            response = requests.get(settings.SEARCH_SERVICE_URL + '/similar', params={
                'dois': dois,
                'limit': total_papers
            })
            response.raise_for_status()
            self._response = response.json()
        except requests.exceptions.Timeout:
            logger.error("Similar Request Connection Timeout")
            self._error = True
        except requests.exceptions.HTTPError:
            self._error = True
        except requests.exceptions.RequestException as e:
            logger.error("Some unknown request exception occured", e)
            self._error = True

        if self._response is None:
            self._error = True

    @property
    def dois(self):
        if not self._result_dois:
            self._result_dois = [result['doi'] for result in self._response['similar']]
        return self._result_dois

    @property
    def paginator(self):
        paper_score_items = [(result['doi'], result['score']) for result in self._response['similar']]
        paper_score_items = sorted(paper_score_items, key=lambda x: x[1], reverse=True)
        paginator = ScoreSortPaginator(paper_score_items, self._papers_per_page)
        return paginator

    @property
    def error(self):
        return self._error