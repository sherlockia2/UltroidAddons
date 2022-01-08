# Ultroid Userbot

"""
Search movie details from IMDB

✘ Commands Available
• `{i}imdb <keyword>`
"""

import aiohttp
from bs4 import BeautifulSoup
import json
import re
from typing import Callable, Coroutine, Dict, List, Tuple, Union
from telethon import Button
from . import *


async def get_content(url):
    async with aiohttp.ClientSession() as session:
        r = await session.get(url)
        return await r.read()

@ultroid_cmd(pattern="imdb ?(.*)")
async def imdb(e):
    await eor(e, "`...`")
    movie_name = e.pattern_match.group(1)
    if not movie_name:
        return await eor(e, "`Provide a movie name too`")
    try:
        await eor(e, "`Processing...`")
        remove_space = movie_name.split(" ")
        query = "+".join(remove_space)
        url = "https://www.imdb.com/find?ref_=nv_sr_fn&q=" + query + "&s=all"
        r = await get_content(url)
        soup = BeautifulSoup(r, "lxml")
        o_ = soup.find("td", {"class": "result_text"})
        if not o_:
            return await eor(e, "`No Results Found, Matching Your Query.`")
        url = "https://www.imdb.com" + o_.find('a').get('href')
        resp = await get_content(url)
        b = BeautifulSoup(resp, "lxml")
        r_json = json.loads(b.find("script", attrs={"type": "application/ld+json"}).contents[0])
        res_str = "**#IMDBRESULT**\n"
        if r_json.get("name"):
            if r_json.get("datePublished"):
                res_str += f"**Name:** `{r_json['name']}`\n`{r_json['datePublished']}` \n"
            else:
                res_str += f"**Name:** `{r_json['name']}` \n"
        if r_json.get("aggregateRating"):
            res_str += f"**Rating ⭐️:** `{r_json['aggregateRating']['ratingValue']}`\n(based on `{r_json['aggregateRating']['ratingCount']}` values) \n"
        if r_json.get("genre"):
            all_genre = r_json['genre']
            genre = "".join(f"{i}, " for i in all_genre)
            genre = genre[:-2]
            res_str += f"**Genres:** `{genre}` \n"
        if r_json.get("actor"):
            all_actors = r_json['actor']
            actors = "".join(f"{i['name']}, " for i in all_actors)
            actors = actors[:-2]
            res_str += f"**Actors:** `{actors}` \n"        
        if r_json.get("description"):
            res_str += f"**Description:** `{r_json['description']}` \n"
        res_str += f"**URL :** {url}"
        thumb = r_json.get('image')
        if thumb:
            await e.delete()
            return await e.client.send_file(e.chat_id, thumb, caption=res_str)  
        await e.edit(res_str)
    except IndexError:
        return await eor(e, "Something went wrong ...")
