from abc import ABC
from pprint import pprint
import requests
from datetime import date

from social_core.backends import google, github, apple

from instagram.tools import generate_code


class GoogleOAuth2(google.GoogleOAuth2, ABC):
    DEFAULT_SCOPE = ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/user.birthday.read']

    def get_user_details(self, response, **kwargs):
        return {'username': response['email'],
                'email': response['email'],
                'first_name': response.get('given_name', ' '),
                'last_name': response.get('family_name', ' '),
                'birthday': self.get_birthday(response),
                'confirm_code': generate_code(),
                }

    def get_birthday(self, response):
        url = f'https://people.googleapis.com/v1/people/{response["sub"]}?personFields=birthdays'
        headers = self.auth_headers()
        headers['Authorization'] = f'Bearer {response["access_token"]}'
        try:
            return date(**self.get_json(url, headers=headers)['birthdays'][0]['date'])
        except KeyError:
            return date(year=1970, month=1, day=1)


class GithubOAuth2(github.GithubOAuth2, ABC):
    DEFAULT_SCOPE = ['user:email', 'read:user']

    def get_user_details(self, response):
        return {'username': response['email'],
                'email': response['email'],
                'first_name': response.get('name', ' '),
                'last_name': response.get('surname', 'GitHub'),
                'birthday': date(year=1970, month=1, day=1),
                'confirm_code': generate_code(),
                }


class AppleIdAuth(apple.AppleIdAuth, ABC):
    # TODO: To finish, add auth by AppleID
    pass
