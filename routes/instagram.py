from dependencies import (
    run_ig_photo_logic, InstaApiException, UserNotFoundException,
)
from fastapi import Response, status
from logger import logger


async def get_ig_photos(username: str, max_count: int, response: Response):
    try:
        urls = await run_ig_photo_logic(username, max_count)
        return {'urls': urls}
    except UserNotFoundException:
        logger.info(f'User {username} not found')
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'User not found'}
    except InstaApiException:
        response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        return {'error': 'Too many requests'}
    except Exception:
        logger.error(f'Internal server error', exc_info=True)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {'error': 'Something get wrong'}
