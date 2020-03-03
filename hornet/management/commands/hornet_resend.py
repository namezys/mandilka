from logging import getLogger

from django.utils.timezone import now

from hornet import models
from hornet import utils
from .common import ClientCommand

logger = getLogger(__name__)

MIN_AGE = 6 * 3600
ONLINE_AGE = 5 * 60

MESSAGES = [
    "Привет. Как дела? Как со свободным временем",
    "Привет. Так что, встретиься то хочешь?",
    "Как настроние? Нашел что интересное? Мы пересечемся?",
    "Чем занят ближайшие дни? Привет",
    "Какие планы на выходные или раньше?",
    "Что нового? Что делаешь?",
    "Хай. Что твори?",
    "Приветики. Когда свооден?",
    "Что в жизни происходит? Привет",
    "Как твои дела?",
]


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument("--update-distance", action="store_true")
        parser.add_argument("--method", choices=["near", "favorites"], default="near")
        parser.add_argument("--online", action="store_true")

    def handle(self, limit, update_distance, method, online, *args, **options):
        if update_distance:
            logger.debug("Reset distance")
            models.Member.objects.update(distance=None)
        member_list = utils.increment_list(self.client.list_favorites, 1000)
        if update_distance:
            utils.update_distance(member_list)
            
        for member in member_list:
            logger.debug("Check member %s", member)
            if online and (now() - member.last_online).total_seconds() > ONLINE_AGE:
                logger.debug("Member is offline. Skip it")
                continue

            messages = sorted(self.client.list_message(member), key=lambda o: o.datetime)
            if messages:
                last_message = messages[-1]
                logger.debug("Last %s", last_message)
                age = now() - last_message.datetime
                logger.debug("Age %s (total seconds %s)", age, age.total_seconds())
                if age.total_seconds() < MIN_AGE:
                    logger.debug("Skip it")
                    continue
            msg = utils.select_and_randomize_msg(MESSAGES)
            logger.debug("Send message: %s", msg)
            self.client.send_message(member, msg)
