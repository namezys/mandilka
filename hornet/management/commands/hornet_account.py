from logging import getLogger

from django.core.management.base import BaseCommand

from hornet.client import Client
from hornet.models import Account

logger = getLogger(__name__)


CREATE = "create"
UPDATE = "update"
PRINT = "print"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("action", choices=[CREATE, UPDATE, PRINT])
        parser.add_argument("username")
        parser.add_argument("--password")
        parser.add_argument("--token")

    def handle(self, username, action, *args, **kwargs):
        account = Account.get_account(username)
        if action == CREATE:
            self.create(account, username, **kwargs)
        elif action == UPDATE:
            self.update(account, **kwargs)
        elif action == PRINT:
            self.print(account)
        else:
            raise AssertionError("Unknown action")

    def create(self, account, username, token, **kwargs):
        if account:
            self.stderr.write("Account exists")
            return
        account = Account.objects.create(username=username, token=token)
        self.stdout.write("Account created")
        self.print(account)

    def update(self, account, token, **kwargs):
        if not account:
            self.stderr.write("Not found")
            return
        account.token = token
        account.save(update_fields=["token"])
        self.print(account)

    def print(self, account):
        if not account:
            self.stderr.write("Not found")
            return
        self.stdout.writelines([
            " pk: %s" % account.pk,
            " username: %s" % account.username,
            " token: %s" % account.token,
        ])


