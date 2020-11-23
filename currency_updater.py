from stasher.utils import scrape_current_amount_of_usd

from run import setup_logging

import logging
import time

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    setup_logging()

    while True:
        logger.info("Currency scrape is starting")
        scrape_current_amount_of_usd()
        time.sleep(16000)
