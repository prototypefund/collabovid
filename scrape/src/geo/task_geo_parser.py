from django.conf import settings

from data.models import GeoCity, GeoCountry, GeoLocation, Paper
from src.geo.paper_geo_extractor import PaperGeoExtractor
from tasks.definitions import register_task, Runnable

from termcolor import colored


@register_task
class GeoParserTask(Runnable):
    @staticmethod
    def task_name():
        return 'parse-geo-locations'

    @staticmethod
    def description():
        return ''

    def __init__(self, *args, **kwargs):
        super(GeoParserTask, self).__init__(*args, **kwargs)

    def run(self):
        n_locations = 0

        with PaperGeoExtractor(db_path=f'{settings.RESOURCES_DIR}/{settings.GEONAMES_DB_REL_PATH}') as geo:
            for paper in Paper.objects.all():
                locations, ignored_entities = geo.extract_locations(paper, recompute_count=False)
                locations = [x for x in locations if x[2] != PaperGeoExtractor.LOCATION_SKIPPED]
                n_locations += len(locations)

                if len(locations) > 0 or len(ignored_entities) > 0:
                    self.log(paper.title)

                    for location in locations:
                        state = 'created' if location[2] == PaperGeoExtractor.LOCATION_CREATED else 'added'
                        self.log(
                            "\t[{:16}] {:20} -> {}".format(colored(state, 'green'), location[1], location[0].name)
                        )

                    for ent in ignored_entities:
                        self.log("\t[{:7}] {:30}".format(colored('ignored', 'red'), ent))

            self.log(f"Recomputing counts.")
            GeoLocation.recompute_counts(GeoCity.objects.all(), GeoCountry.objects.all())
            self.log(f"Recomputed counts")

        self.log(f"Added {n_locations} locations")