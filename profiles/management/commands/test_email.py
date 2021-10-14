from django.core.management.base import BaseCommand
from profiles.emails import test_email

class Command(BaseCommand):
    help = 'Send available e-mails for testing purpose.'

    def add_arguments(self, parser):
        parser.add_argument('email', help='E-mail to send to')

    def handle(self, *args, **kwargs):
        test_email(kwargs['email']).send()
