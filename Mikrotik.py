from librouteros import connect
from librouteros.query import Key
import re


def parse_uptime(uptime):
    weeks = 0
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    weeks_parse = re.search('(?:(\d+)w)', uptime)
    days_parse = re.search('(?:(\d+)d)', uptime)
    hours_parse = re.search('(?:(\d+)h)', uptime)
    minutes_parse = re.search('(?:(\d+)m)', uptime)
    seconds_parse = re.search('(?:(\d+)s)', uptime)
    if weeks_parse:
        try:
            weeks = int(weeks_parse.group().replace('w', ''))
        except:
            pass
    if days_parse:
        try:
            days = int(days_parse.group().replace('d', ''))
        except:
            pass
    if hours_parse:
        try:
            hours = int(hours_parse.group().replace('h', ''))
        except:
            pass
    if minutes_parse:
        try:
            minutes = int(minutes_parse.group().replace('m', ''))
        except:
            pass
    if seconds_parse:
        try:
            seconds = int(seconds_parse.group().replace('s', ''))
        except:
            pass

    days += weeks * 7
    hours += days * 24
    minutes += hours * 60
    seconds += minutes * 60

    return seconds


class Mikrotik:

    def __init__(self):
        self.error = None
        self.api = None

    def connect(self, host: str, username: str, password: str, port: int) -> object:
        self.api = None
        try:
            self.api = connect(username=username, password=password, port=port, host=host)
            return self
        except Exception as error:
            self.error = error
            return self

    def close(self):
        self.api.disconnect()

    def get_all_bgp_peers(self):
        try:
            data = []
            bgp_peer_path = self.api.path('routing', 'bgp', 'peer').select(
                Key('name'),
                Key('remote-as'),
                Key('remote-address'),
            ).where(
                Key('disabled') == False
            )

            for peer in tuple(bgp_peer_path):
                peer_info = {"{#PEER_NAME}": peer['name'], "{#PEER_AS}": peer['remote-as'],
                             "{#PEER_ADDR}": peer['remote-address']}
                data.append(peer_info)

            return {"data": data}
        except Exception as error:
            self.error = error

    def get_bgp_peer_info(self, peer_name, get_advertisements=False):
        try:
            bgp_peer_path = self.api.path('routing', 'bgp', 'peer')

            peer_info = tuple(bgp_peer_path.select(
                Key('name'),
                Key('instance'),
                Key('disabled'),
                Key('remote-address'),
                Key('remote-as'),
                Key('uptime'),
                Key('established'),
                Key('prefix-count')
            ).where(
                Key('name') == peer_name,
                Key('disabled') == False
            ))[0]

            if not peer_info:
                return None

            if 'established' in peer_info and peer_info['established']:
                peer_info['uptime'] = parse_uptime(peer_info['uptime'])

            peer_info['established'] = 1 if 'established' in peer_info and peer_info['established'] else 0

            if get_advertisements:
                peer_info['advertisements'] = len(self.get_bgp_peer_advertisements(peer_name))
            return {"data": peer_info}
        except Exception as error:
            self.error = error

    def get_bgp_peer_advertisements(self, peer_name):
        try:
            bgp_peer_advertisements_path = self.api.path('routing', 'bgp', 'advertisements')

            peer_advertisements = tuple(bgp_peer_advertisements_path.select(
                Key('peer'),
                Key('prefix'),
                Key('nexthop')
            ).where(
                Key('peer') == peer_name
            ))

            return peer_advertisements if peer_advertisements else tuple()
        except Exception as error:
            self.error = error
