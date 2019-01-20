# TODO Could check users levels for the kanji/radicals under review to see if they are
# gurued yet
# Should be able to make a large filter query to assignments and check there
import asyncio
import aiosqlite
import time
import aiohttp
from config import *

async def get_summary(session, wk_api_key):
    auth_header = {'Authorization': 'Bearer {0}'.format(wk_api_key)}
    resp = await session.get('https://api.wanikani.com/v2/summary', headers=auth_header)
    summary = await resp.json()
    current_review_time = summary['data_updated_at']
    current_reviews_ids = summary['data']['reviews'][0]['subject_ids']
    return current_review_time, current_reviews_ids

async def get_current_level_items(current_reviews_ids):
    pass

async def process_user(session, db, user):
    # Call get summary, if no reviews, skip
    current_review_time, current_reviews_ids = await get_summary(session, user['wk_api_key'])
    print(current_review_time)
    print(current_reviews_ids)
    # Call get assignments since last alert date, if none, skip
    # Check current ids from summary against DB for current level check
    # If current level, send alert
    pass

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def get_users(db):
    db.row_factory = dict_factory
    cursor = await db.execute("SELECT * from account")
    res = await cursor.fetchall()
    print(res)
    return res

async def create_tasks():
    # Get users from db
    # loop through and use each key, also need pushover key
    # TODO Use wk_api_key and pushover from db
    wk_api_key = my_wk_api_key
    pushover_user_key = my_pushover_api_key
    async with aiohttp.ClientSession() as session:
        async with aiosqlite.connect('wk_push.db') as db:
            # create tasks
            # TODO Should return list of task objects, then we can gather them
            users = await get_users(db)
            tasks = []
            for user in users:
                task = asyncio.create_task(process_user(session, db, user))
                tasks.append(task)
            # await process_user(session, db, wk_api_key, pushover_user_key)
            await asyncio.gather(*tasks)

            # Await all tasks
            # await asyncio.gather(get_summary(session, wk_api_key))

# asyncio.run(get_summary())
start = time.time()
asyncio.run(create_tasks())
end = time.time()
print(str(end - start) + " seconds")