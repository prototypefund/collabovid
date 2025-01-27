import re
import time

import arxiv
import datetime
import calendar

from nameparser import HumanName

from data.models import DataSource
from src.updater.data_updater import DataUpdater
from data.paper_db_insert import SerializableArticleRecord

_ARXIV_PAPERHOST_NAME = 'arXiv'


def _get_arxiv_id_from_url(url):
    reduced_url = re.sub(r'v(\d+)$', '', url)
    splits = reduced_url.split('/abs/')
    if len(splits) < 2:
        return None
    else:
        return 'arXiv:' + splits[1]


class ArxivUpdater(DataUpdater):
    """
    Updater class for the arXiv data source.
    """
    _ARXIV_SEARCH_QUERY = 'title:"COVID 19" OR title:"SARS-CoV-2" OR title:"coronavirus" ' \
                          'OR abs:"COVID 19" OR abs:"SARS-CoV-2" OR abs:"coronavirus"'

    def __init__(self, log=print, pdf_image=False, pdf_content=False, update_existing=False, force_update=False):
        super().__init__(log, pdf_image=pdf_image, pdf_content=pdf_content,
                         update_existing=update_existing, force_update=force_update)
        self._query_result = None

    @staticmethod
    def _get_datetime(time_val):
        if isinstance(time_val, time.struct_time):
            return datetime.datetime.fromtimestamp(calendar.timegm(time_val), tz=datetime.timezone.utc)
        else:
            return time_val

    @property
    def data_source(self):
        return DataSource.ARXIV

    def _load_query_result(self):
        if not self._query_result:
            query_result = arxiv.Search(self._ARXIV_SEARCH_QUERY,
                                        sort_by=arxiv.SortCriterion.SubmittedDate,
                                        sort_order=arxiv.SortOrder.Descending)
            self._query_result = [x for x in query_result.results()
                                  if self._get_datetime(x.updated).date() >= datetime.date(2019, 12, 1)]

    def _count(self):
        self._load_query_result()
        return len(self._query_result)

    def _extract_authors(self, raw_data: arxiv.Result):
        authors = []
        for author in raw_data.authors:
            human_name = HumanName(author.name)
            first_name = f'{human_name.first} {human_name.middle}'.replace(';', '').replace(',', '').strip()
            last_name = human_name.last.replace(';', '').replace(',', '').strip()
            if first_name or last_name:
                authors.append((last_name, first_name))
        return authors

    def _create_serializable_record(self, raw_data: arxiv.Result):
        """ Construct a serializable record from a given result of the arxiv package """
        article = SerializableArticleRecord(doi=_get_arxiv_id_from_url(raw_data.entry_id),
                                            title=raw_data.title.replace('\n', ' '),
                                            abstract=raw_data.summary.replace('\n', ' '),
                                            is_preprint=True)
        article.paperhost = _ARXIV_PAPERHOST_NAME
        article.datasource = DataSource.ARXIV
        article.url = raw_data.entry_id
        article.publication_date = self._get_datetime(raw_data.published).date()

        version_match = re.match('^\S+v(\d+)$', raw_data.entry_id)
        if version_match:
            article.version = version_match.group(1)
        else:
            article.version = '1'

        article.pdf_url = raw_data.pdf_url
        article.authors = self._extract_authors(raw_data)

        return article

    def _get_data_points(self):
        self._load_query_result()
        for article in self._query_result:
            yield self._create_serializable_record(raw_data=article)

    def _get_data_point(self, doi):
        self._load_query_result()
        try:
            return self._create_serializable_record(next(x for x in self._query_result
                                                         if _get_arxiv_id_from_url(x['id']) == doi))
        except StopIteration:
            return None
