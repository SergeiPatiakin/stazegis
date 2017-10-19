from django.core.management.base import BaseCommand
from geoserver_rest.geoserver_rest import cleanup_server, setup_server

class Command(BaseCommand):
    help = 'Sets up geoserver through the REST API'

    def handle(self, *args, **options):
        cleanup_server()
        setup_server()
        print("Geoserver setup successful")