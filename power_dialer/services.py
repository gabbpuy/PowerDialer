# -*- coding: utf-8 -*-
import logging
import random
logger = logging.getLogger('power_dialer.services')


def dial(agent_id: str, lead_phone_number: str):
    logger.info('Dialing %s for %s', agent_id, lead_phone_number)


def _generateNPA() -> str:
    first = random.randint(2, 9)
    second = random.randint(0, 8)
    third = random.randint(0, 9)
    # Not going to check for easily recognizable codes (ERC)
    return f'{first}{second}{third}'


def _generate_central_office_code() -> str:
    first = random.randint(2, 9)
    second = random.randint(0, 9)
    third = random.randint(0, 9)
    while second == 1 and third == 1:
        third = random.randint(0, 9)
    return f'{first}{second}{third}'


def _generate_line_number() -> str:
    number = random.randint(0, 9999)
    return f'{number:04}'


def get_lead_phone_number_to_dial() -> str:
    """
    Return a phone number (mostly) conforming to a 10 digit North American Numbering Plan (NANP)
    The NANP number format may be summarized in the notation NPA-NXX-xxxx:

    :return: A string representing a phone number
    """
    npa = _generateNPA()
    coc = _generate_central_office_code()
    line = _generate_line_number()
    # Make it human readable for testability
    return f'({npa}) {coc}-{line}'
