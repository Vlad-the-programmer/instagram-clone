# management/commands/wait_for_db.py
import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Waits for database to be available'

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        max_retries = 30
        retry_count = 0

        while retry_count < max_retries:
            try:
                connections['default'].ensure_connection()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
                retry_count += 1

        self.stdout.write(self.style.ERROR('Max retries reached. Database still not available.'))
        raise OperationalError('Could not connect to database after 30 seconds')