"""
Runs a given task or returns a list of available tasks for this service.
"""
import os
import argparse
import json
import django

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scrape.settings_dev')
    django.setup()

    from src.scrape import *
    from src.pdf_content_scraper import *
    from src.medrxiv_scraping_task import *
    from src.citation_refresher import *
    from src.pdf_image_scraper import *
    from src.pdf_scraper import *
    from tasks.definitions import SERVICE_TASKS, SERVICE_TASK_DEFINITIONS
    from tasks.task_runner import TaskRunner

    parser = argparse.ArgumentParser()
    parser.add_argument('task', nargs='?', default=None)
    parser.add_argument('-u', '--user', default='default')
    parser.add_argument('-l', '--list', action='store_true')

    args = parser.parse_args()

    if args.list:
        with open('tasks.json', 'w') as f:
            json.dump(SERVICE_TASK_DEFINITIONS, f)
    else:

        task_name = args.task

        if task_name not in SERVICE_TASKS:
            print('Error Unknown Task: ', args.task)
            exit(1)
        task_cls = SERVICE_TASKS[task_name]
        TaskRunner.run_task(task_cls, started_by=args.user)

