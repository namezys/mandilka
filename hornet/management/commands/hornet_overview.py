from logging import getLogger

from django.utils.timezone import now

from hornet import utils
from .common import ClientCommand

logger = getLogger(__name__)

MIN_AGE = 6 * 3600
ONLINE_AGE = 5 * 60

MESSAGES = [
    "Привет. Познакомимся?",
    "Привет. Как дела? Чем занят?",
    "Знакомиься будем? Привет",
    "Давай знакомиьтся. Что ищешь тут?",
    "Здорово. Познакомимся поближе?",
    "Привет. Как весеннее настроение?",
]


class Command(ClientCommand):

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=200)
        parser.add_argument("--update-distance", action="store_true")
        parser.add_argument("--method", choices=["near", "favorites"], default="near")
        parser.add_argument("--distance", type=float, default=35)
        parser.add_argument("--online", action="store_true")

    def handle(self, limit, update_distance, method, distance, online, *args, **options):
        member_list = utils.increment_list(self.client.list_near, 9000)
        logger.debug("Got %s members", len(member_list))
        utils.update_distance(member_list)
        member_list = [i for i in member_list if i.distance is not None and i.distance <= distance]
        logger.debug("Got %s filtered members", len(member_list))
            
        for member in member_list:
            logger.debug("Check member %s", member)
            if online and (now() - member.last_online).total_seconds() > ONLINE_AGE:
                logger.debug("Member is offline. Skip it")
                continue

            messages = sorted(self.client.list_message(member), key=lambda o: o.datetime)
            if messages:
                if len(messages) >= 2:
                    logger.debug("Too much messages. Skip")
                    continue
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
