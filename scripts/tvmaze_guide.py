"""Partial TVmaze episode schedules, mapped by reviewed network IDs.

Data: TVmaze, CC BY-SA 4.0. No inferred runtimes, reruns, station matches or shows.
"""
from datetime import datetime, timedelta, timezone
import json
from urllib.parse import urlencode, urlsplit

LICENSE = 'https://creativecommons.org/licenses/by-sa/4.0/'


def collect(provider, fetcher, now):
    if provider['url'] != 'https://api.tvmaze.com/schedule':
        raise ValueError('TVmaze adapter requires the documented schedule endpoint')
    country = provider.get('country')
    if country not in {'US'}:
        raise ValueError('Country requires an explicit review before enabling')
    episodes = []
    # Prior date handles overnight broadcasts and UTC/local date boundaries.
    for offset in range(-1, 3):
        day = (now.astimezone(timezone.utc)+timedelta(days=offset)).date().isoformat()
        raw = json.loads(fetcher(provider['url']+'?'+urlencode({'country':country,'date':day})))
        if not isinstance(raw, list) or len(raw)>10000:
            raise ValueError('Unexpected TVmaze schedule response')
        episodes.extend(raw)
    return normalize(episodes, provider)


def normalize(episodes, provider):
    channels = {}
    source = provider['id']
    for episode in episodes:
        if not isinstance(episode, dict):
            continue
        show = episode.get('show')
        if not isinstance(show, dict):
            continue
        network = show.get('network')
        if not isinstance(network, dict):
            continue
        network_id = str(network.get('id'))
        channel = provider['channelMap'].get(network_id)
        country = network.get('country')
        if (not isinstance(country,dict) or not channel or network.get('name') != provider['networkNames'].get(network_id)
                or country.get('code') != provider['country']):
            continue
        title = show.get('name')
        duration = episode.get('runtime')
        if not isinstance(title, str) or not title.strip() or len(title)>220:
            continue
        if type(duration) not in (int, float) or not 0<duration<=720:
            continue
        try:
            start = datetime.fromisoformat(episode.get('airstamp','').replace('Z','+00:00'))
            if start.tzinfo is None:
                continue
            start = start.astimezone(timezone.utc)
            stop = start+timedelta(minutes=duration)
        except (ValueError, TypeError, OverflowError):
            continue
        episode_title = episode.get('name')
        if isinstance(episode_title,str) and episode_title.strip() and len(episode_title)<150:
            title += ' · '+episode_title.strip()
        programme = {'title':title,'start':start.isoformat().replace('+00:00','Z'),
                     'stop':stop.isoformat().replace('+00:00','Z'),'source':source}
        url = episode.get('url')
        if isinstance(url,str) and urlsplit(url).scheme=='https' and urlsplit(url).netloc=='www.tvmaze.com':
            programme['url'] = url
        channels.setdefault(channel,[]).append(programme)
    for channel, programmes in channels.items():
        unique={(p['start'],p['stop'],p['title']):p for p in programmes}
        channels[channel]=sorted(unique.values(),key=lambda p:p['start'])
    return {'channels':channels}
