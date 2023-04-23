
__all__ = ('DJANGO_CONFIG', 'DATABASE_CONFIG', 'GOOGLE_AUTH_CONFIG', 'GITHUB_AUTH_CONFIG')

from pathlib import Path
import json

BASE_DIR = Path(__file__).parents[3]
CONFIG_DIR = BASE_DIR / 'etc'
CONFIG_DIR.mkdir(exist_ok=True)
DJANGO_FILE_CONFIG = CONFIG_DIR / 'django_config.json'

default_config_JSON = {

    "DEBUG": "True",
    "SECRET_KEY": "django-insecure-_____________________to_change____________________",
    "EMAIL": "",
    "EMAIL_PASSWORD": "",
    "ALLOWED_HOSTS": ('127.0.0.1',),
    "OWM_TOKEN_KEY": "",
    "FREQUENCY_UPDATE_DATA": {
        "hours": 1,
        "minutes": 0
    },

    "DATABASE": {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'database.sqlite3'),
            'TEST': {'NAME': ':memory:', "ENGINE": "django.db.backends.sqlite3"}
        }
    },

    "GOOGLE_AUTH": {
        "web": {
            "client_id": "",
            "project_id": "",
            "auth_uri": "",
            "token_uri": "",
            "auth_provider_x509_cert_url": "",
            "client_secret": ""
        }
    },

    "GITHUB_AUTH": {
        "DEV": {
            "client_id": "",
            "client_secret": ""
        },
        "PROD": {
            "client_id": "",
            "client_secret": ""
        }
    }
}

# Write default settings (write)
if not DJANGO_FILE_CONFIG.exists():
    with DJANGO_FILE_CONFIG.open(mode='w') as js_file:
        json.dump(default_config_JSON, js_file, indent=4)

# Loadings (output)
with DJANGO_FILE_CONFIG.open(mode='r') as js_file:
    DJANGO_CONFIG = json.load(js_file)

DATABASE_CONFIG = DJANGO_CONFIG['DATABASE']
GOOGLE_AUTH_CONFIG = DJANGO_CONFIG['GOOGLE_AUTH']
GITHUB_AUTH_CONFIG = DJANGO_CONFIG['GITHUB_AUTH']

