import asyncio
from aiohttp.client import ClientSession
import json
from logger import logger


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/114.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-IG-App-ID': '936619743392459'  # Didn't change at least from summer 2022
}

PAGE_LIMIT = 12
MAX_POSTS_AMOUNT = 31
IG_MEDIA_URL = 'https://www.instagram.com/graphql/query/' \
               '?query_hash=e769aa130647d2354c40ea6a439bfc08&variables={}'
SLEEP_TIME = 3
USERNAME = 'sh.ruby.cow'


class InstaApiException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class InstaApiHandler:

    def __init__(self, session: ClientSession, sleep_time=SLEEP_TIME):
        self.session = session
        self.sleep_time = sleep_time

    async def __get(self, url: str):
        logger.info(f'Request: {url}')
        response = await self.session.get(url)
        if response.status == 404:
            raise UserNotFoundException()
        if response.status != 200:
            error = await response.text()
            logger.error(
                f'Request error. '
                f'Url: {url}. '
                f'Status code: {response.status}. '
                f'Error: {error}'
            )
            raise InstaApiException(error)

        json_data = await response.json()

        await asyncio.sleep(self.sleep_time)
        return json_data

    async def get_user(self, username: str) -> dict:
        url = f'https://www.instagram.com/api/v1' \
              f'/users/web_profile_info/?username={username}'
        return await self.__get(url)

    async def get_media(self, variables: dict):
        variables_json = json.dumps(variables)
        url = IG_MEDIA_URL.format(variables_json)
        return await self.__get(url)


async def process_media(media_data: list) -> list:
    page_urls = []
    for edge in media_data:
        typename = edge['node']['__typename']
        if typename == 'GraphSidecar':
            children = edge['node']['edge_sidecar_to_children']['edges']
            children_urls = [node['node']['display_url'] for node in children]
            page_urls.append(children_urls)
        elif typename == 'GraphImage':
            page_urls.append([edge['node']['display_url']])
    return page_urls


async def run_ig_photo_logic(username: str, max_count: int):
    async with ClientSession(headers=HEADERS) as session:
        api_handler = InstaApiHandler(session)
        user_info = await api_handler.get_user(username)
        user_id = user_info['data']['user']['id']

        by_page_urls = []
        variables = {'id': user_id, 'first': PAGE_LIMIT}
        _page_index = 1
        while True:
            media_response_json = await api_handler.get_media(variables)

            useful_data = media_response_json['data']['user'][
                'edge_owner_to_timeline_media'
            ]
            media_data = useful_data['edges']
            page_info = useful_data['page_info']

            page_img_urls = await process_media(media_data)
            len_all, len_page = len(by_page_urls), len(page_img_urls)
            if len_all + len_page < max_count:
                by_page_urls.extend(page_img_urls)
            else:
                by_page_urls.extend(page_img_urls[:max_count-len_all])
                break

            if not page_info['has_next_page']:
                break

            variables['after'] = page_info['end_cursor']
            _page_index += 1

    result_urls = []
    [result_urls.extend(url_by_page) for url_by_page in by_page_urls]
    return result_urls

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_ig_photo_logic(
        'sfansjkfbasjbfjasfbjasfk',
        MAX_POSTS_AMOUNT)
    )
