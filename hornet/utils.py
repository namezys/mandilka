import random
from logging import getLogger

logger = getLogger(__name__)


def increment_list(method, limit):
    logger.info("Increment download ")
    member_list = []
    page_number = 0
    while len(member_list) < limit:
        logger.debug("Load page: %s", page_number)
        call_result = method(page_number, 100)
        if not call_result:
            logger.debug("No new result. Stop")
            break
        member_list.extend(call_result)
        logger.debug("Loaded %s members", len(member_list))
        page_number += 1
    return member_list


def update_distance(member_list):
    logger.info("Update distance for %s members", len(member_list))
    if member_list[0].distance is None:
        logger.debug("Treat distance of first member as 0")
        member_list[0].distance = 0
        member_list[0].save()

    for idx in range(1, len(member_list) - 1):
        if member_list[idx].distance is not None:
            continue
        member = member_list[idx]
        logger.debug("Found %s at idx %s without distance", member, idx)
        prev_member = member_list[idx - 1]
        next_member = None

        for next_idx in range(idx + 1, len(member_list)):
            if member_list[next_idx].distance is not None:
                logger.debug("Next member at %s", next_idx)
                next_member = member_list[next_idx]
                break

        if next_member:
            logger.debug("Update member distance to middle")
            member.distance = (prev_member.distance + next_member.distance) / 2
            member.save()
        else:
            logger.debug("Update member distance to previous")
            member.distance = prev_member.distance
            member.save()


def randomize_msg(msg):
    idx = random.randint(0, len(msg) - 1)
    return msg[0:idx] + msg[idx + 1:]


def select_and_randomize_msg(messages):
    return randomize_msg(random.choice(messages))
