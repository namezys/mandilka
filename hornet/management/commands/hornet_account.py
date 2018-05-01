from logging import getLogger

from django.core.management.base import BaseCommand

from hornet.client import Client
from hornet.models import Account

logger = getLogger(__name__)


CREATE = "create"
UPDATE = "update"
PRINT = "print"
LOGIN = "login"


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("action", choices=[CREATE, UPDATE, PRINT, LOGIN])
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
        elif action == LOGIN:
            self.login(account)
        else:
            raise AssertionError("Unknown action")

    def create(self, account, username, token, password, **kwargs):
        if account:
            self.stderr.write("Account exists")
            return
        account = Account.objects.create(username=username, token=token, password=password)
        self.stdout.write("Account created")
        self.print(account)

    def update(self, account, token, password, **kwargs):
        if not account:
            self.stderr.write("Account not found")
            return
        update_fields = []
        if token is not None:
            account.token = token
            update_fields += ["token"]
        if password is not None:
            account.password = password
            update_fields += ["password"]
        account.save(update_fields=update_fields)
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

    def login(self, account):
        if not account:
            self.stderr.write("Account not found")
            return
        if not account.password:
            self.stderr.write("Unknown password")
            return
        client = Client(account)
        account.token = client.login()
        account.save(update_fields=["token"])


