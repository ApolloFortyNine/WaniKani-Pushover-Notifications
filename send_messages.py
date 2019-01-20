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
    return current_reviews_ids

async def get_current_level_items(db, current_reviews_ids):
    sql_placeholder = '?'
    placeholders = ', '.join(sql_placeholder for _ in current_reviews_ids)
    query = "SELECT id FROM wk_subject WHERE id in ({0}) AND subject_level=23 AND subject_object in ('kanji', 'radical')".format(placeholders)
    cursor = await db.execute(query, current_reviews_ids)
    res = await cursor.fetchall()
    print(res)
    return res

async def get_user_level(session, wk_api_key):
    auth_header = {'Authorization': 'Bearer {0}'.format(wk_api_key)}
    resp = await session.get('https://api.wanikani.com/v2/user', headers=auth_header)
    user = await resp.json()
    user_current_level = user['data']['level']
    user_last_review_time = user['data_updated_at']
    return user_current_level, user_last_review_time

async def get_unpassed_items(session, wk_api_key, current_reviews_ids, user_current_level):
    auth_header = {'Authorization': 'Bearer {0}'.format(wk_api_key)}
    subject_ids = ','.join(str(x) for x in current_reviews_ids)
    subject_types = 'kanji,radical'
    params = {'subject_ids': subject_ids, 'levels': user_current_level, 'subject_types': subject_types}
    resp = await session.get('https://api.wanikani.com/v2/assignments', headers=auth_header, params=params)
    assignments = await resp.json()
    kanji_count = 0
    radical_count = 0
    for assignment in assignments['data']:
        if not assignment['data']['passed']:
            if assignment['data']['subject_type'] == 'kanji':
                kanji_count += 1
            elif assignment['data']['subject_type'] == 'radical':
                radical_count += 1
    return radical_count, kanji_count

async def send_pushover_notification(session, db, pushover_user_key, radical_count, kanji_count):
    total_pending = kanji_count + radical_count
    message = "You have {0} pending priority reviews. Radicals: {1} | Kanji: {2}".format(total_pending, radical_count, kanji_count)
    wk_review_link = 'https://www.wanikani.com/review'
    payload = {'token': pushover_application_key, 'user': pushover_user_key, 'message': message, 'url': wk_review_link, 'url_title': 'Review Now'}
    resp = await session.post('https://api.pushover.net/1/messages.json', json=payload)
    if resp.status == 200:
        return True

async def set_last_alert_ts(db, user_id, user_last_review_time):
    await db.execute("UPDATE account SET last_review_ts=? WHERE id=?", [user_last_review_time, user_id])
    await db.commit()

async def process_user(session, db, user):
    # Call get summary, if no reviews, skip
    user_current_level, user_last_review_time = await get_user_level(session, user['wk_api_key'])
    if user_last_review_time == user['last_review_ts']:
        return
    current_reviews_ids = await get_summary(session, user['wk_api_key'])
    print(current_reviews_ids)
    radical_count, kanji_count = await get_unpassed_items(session, user['wk_api_key'], current_reviews_ids, user_current_level)
    print(kanji_count)
    print(radical_count)
    if kanji_count or radical_count:
        sent = await send_pushover_notification(session, db, user['pushover_user_key'], radical_count, kanji_count)
        if sent:
            await set_last_alert_ts(db, user['id'], user_last_review_time)
    # current_level_ids = await get_current_level_items(db, current_reviews_ids)
    # Call get assignments since last alert date, if none, skip
    # Check current ids from summary against DB for current level check
    # If current level, send alert

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

async def get_users(db):
    cursor = await db.execute("SELECT * from account")
    res = await cursor.fetchall()
    print(res)
    return res


async def create_tasks():
    # Get users from db
    # loop through and use each key, also need pushover key
    # TODO Use wk_api_key and pushover from db
    async with aiohttp.ClientSession() as session:
        async with aiosqlite.connect('wk_push.db') as db:
            db.row_factory = dict_factory
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