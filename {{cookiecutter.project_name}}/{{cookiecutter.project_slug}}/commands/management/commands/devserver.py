import os
import subprocess

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Runs Django dev server along with optional Celery using docker/dev_entrypoint.sh'

    def handle(self, *args, **options):
        script = os.path.join(os.getcwd(), 'docker/dev_entrypoint.sh')
        if not os.path.isfile(script):
            self.stderr.write(self.style.ERROR(f'{script} not found'))
            return

        try:
            subprocess.call(['sh', script])
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('Shutting down...'))
