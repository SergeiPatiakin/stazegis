import os

GEOSERVER_REST_ENDPOINT = os.environ.get("GEOSERVER_REST_ENDPOINT")
GEOSERVER_REST_USERNAME = os.environ.get("GEOSERVER_REST_USERNAME", "admin")
GEOSERVER_REST_PASSWORD = os.environ.get("GEOSERVER_REST_PASSWORD", "geoserver")

# DEBUG=False unless DEBUG environment variable is set to True (case-insensitive)
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT', "5432")
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

SECRET_KEY = os.environ.get('SECRET_KEY')