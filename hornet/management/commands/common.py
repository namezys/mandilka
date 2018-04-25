from logging import getLogger

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.utils.functional import cached_property

from hornet.client import Client
from hornet.models import Account

logger = getLogger(__name__)


class ClientCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(stdout=None, stderr=None, no_color=False)
        self._account_username = None

    def create_parser(self, prog_name, subcommand):
        parser = super(ClientCommand, self).create_parser(prog_name, subcommand)
        parser.add_argument("--account", type=int)
        return parser

    def execute(self, *args, **options):
        self._account_username = options.pop("account", None)
        super().execute(*args, **options)

    @cached_property
    def client(self):
        if self._account_username:
            account = Account.get_account(self._account_username)
        else:
            account = Account.objects.first()

        if not account:
            raise CommandError("Account doesn't found")

        return Client(account)

    def handle(self, *args, **options):
        super(ClientCommand, self).handle(*args, **options)
