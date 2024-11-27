# import os
# from celery import Celery
# from celery.schedules import crontab


# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_scraper.settings')

# app = Celery('car_scraper')
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

# # Schedule the scraping task to run every 10 hours
# app.conf.beat_schedule = {
#     'scrape-cars-every-800-seconds': {
#         'task': 'scraper.tasks.scrape_cars',
#         'schedule': 800.0,  # 30 seconds interval
#     },
# }


import os
from celery import Celery
from celery.schedules import crontab
from celery.app.control import Inspect

# Set default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'car_scraper.settings')

# Initialize Celery app
app = Celery('car_scraper')

# Load settings from Django settings with namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all registered Django apps
app.autodiscover_tasks()


app.conf.beat_schedule = {
        'scrape-cars-every-minute': {
            'task': 'scraper.tasks.scrape_cars',
            'schedule': 32400.0,  # Run every 60 seconds (1 minute)
        },
    }
    # Reload the beat schedule
app.conf.update()