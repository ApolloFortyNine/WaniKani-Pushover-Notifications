# Check if cache has been updated, if so, dump table and reinsert. Run at
# 4:30am.
# We can do future case of if I have more than X reviews and what not

import asyncio
import aiohttp
import aiosqlite
import time
from config import my_wk_api_key

async def process_subjects(session, db):
    cursor = await db.execute("SELECT cache_string FROM wk_subject_info WHERE id=1")
    row = await cursor.fetchone()
    await cursor.close()
    if row:
        cache_string = row[0]
    else:
        cache_string = ''
    headers = {'Authorization': 'Bearer {0}'.format(my_wk_api_key), 'If-None-Match': '{0}'.format(cache_string)}
    resp = await session.get("https://api.wanikani.com/v2/subjects", headers=headers)
    if resp.status == 304:
        return
    await db.execute("DELETE FROM wk_subject")
    subject_resp = await resp.json()
    await insert_records(db, subject_resp)
    next_page = subject_resp['pages']['next_url']
    while next_page:
        resp = await session.get(next_page, headers=headers)
        subject_resp = await resp.json()
        await insert_records(db, subject_resp)
        next_page = subject_resp['pages']['next_url']

    cache_string = resp.headers['Etag']
    await db.execute("DELETE FROM wk_subject_info")
    await db.execute("INSERT INTO wk_subject_info (id, cache_string) VALUES (1, '{0}')".format(cache_string))
    await db.commit()

async def insert_records(db, subject_resp):
    formatted_subject_arr = []
    for subject in subject_resp['data']:
        subject_id = subject['id']
        level = subject['data']['level']
        subject_object = subject['object']
        formatted_subject_arr.append((subject_id, level, subject_object))
    await db.executemany('INSERT INTO wk_subject (id, subject_level, subject_object) VALUES (?,?,?)', formatted_subject_arr)
    await db.commit()
    


async def main():
    async with aiohttp.ClientSession() as session:
        async with aiosqlite.connect('wk_push.db') as db:
            await process_subjects(session, db)

start = time.time()
asyncio.run(main())
end = time.time()
print(str(end - start) + " seconds")