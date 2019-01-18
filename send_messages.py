import asyncio
import time
import aiohttp
from config import *

async def get_summary(session, wk_api_key):
    auth_header = {'Authorization': 'Bearer {0}'.format(wk_api_key)}
    resp = await session.get('https://api.wanikani.com/v2/summary', headers=auth_header)
    print(resp.status)
    summary = await resp.json()
    current_time = summary['data_updated_at']
    current_reviews_ids = summary['data']['reviews'][0]['subject_ids']
    return current_time, current_reviews_ids

async def process_users(session, wk_api_key, pushover_user_key):
    # Call get summary, if no reviews, skip
    current_time, current_reviews_ids = await get_summary(session, wk_api_key)
    # Call get assignments since last alert date, if none, skip
    # Check current ids from summary against DB for current level check
    # If current level, send alert
    pass

async def create_tasks():
    # Get users from db
    # loop through and use each key, also need pushover key
    # TODO Use wk_api_key and pushover from db
    wk_api_key = my_wk_api_key
    pushover_user_key = my_pushover_api_key
    async with aiohttp.ClientSession() as session:

        # create tasks
        # TODO Should return list of task objects, then we can gather them
        await process_users(session, wk_api_key, pushover_user_key)

        # Await all tasks
        # await asyncio.gather(get_summary(session, wk_api_key))

# asyncio.run(get_summary())
start = time.time()
asyncio.run(create_tasks())
end = time.time()
print(str(end - start) + " seconds")