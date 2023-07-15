import logging

logger = logging.getLogger(__name__)
handler = logging.FileHandler('instagram.log', encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
