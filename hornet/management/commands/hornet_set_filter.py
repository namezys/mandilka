from logging import getLogger

from .common import ClientCommand

logger = getLogger(__name__)


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("min_age", type=int)
        parser.add_argument("max_age", type=int)

    def handle(self, min_age, max_age, *args, **kwargs):
        self.client.set_filter(min_age, max_age)
