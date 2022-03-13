#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime, date
from urllib.parse import urljoin
from dataclasses import dataclass, asdict
import requests
from bs4 import BeautifulSoup, Tag
from time import sleep
from pathlib import Path

WEBHOOK = os.environ['WEBHOOK']
QUEUE = 'atcoder_alert.json'

@dataclass(frozen=True)
class Contest:
    timestamp: int = 0
    url: str = 'https://atcoder.jp/contests/'
    title: str = 'undefined'

    @classmethod
    def from_tr(cls, tr: Tag):
        tds = tr.select('td')
        time_text = re.sub(r'\+.*', '', tds[0].text.strip())
        link = tds[1].select_one('a')
        timestamp = int(datetime.fromisoformat(time_text).timestamp())
        url = urljoin('https://atcoder.jp/', link['href'])
        title = link.text.strip()
        return cls(timestamp, url, title)
    
    def __lt__(self, x:'Contest'):
        return self.timestamp < x.timestamp
    def __le__(self, x:'Contest'):
        return self.timestamp <= x.timestamp
    def __gt__(self, x:'Contest'):
        return self.timestamp > x.timestamp
    def __ge__(self, x:'Contest'):
        return self.timestamp >= x.timestamp


class AtCoderAlert:
    UNIT_SEC = 60

    def __init__(self):
        self.jobs:set[Contest] = set()
        self.prev = datetime.fromtimestamp(0)
    
    def run(self):
        while True:
            self.every_unit()
            sleep(self.UNIT_SEC)
    
    def every_unit(self):
        if self.prev.date() < date.today():
            self.every_day()
        self.check_queue()
        self.write_queue()
    
    def every_day(self):
        self.check_schedule()
    
    def check_schedule(self):
        res = requests.get('https://atcoder.jp/contests/?lang=ja')
        soup = BeautifulSoup(res.content, 'lxml')
        for tr in soup.select('#contest-table-upcoming tbody tr'):
            try:
                con = Contest.from_tr(tr)
                if 'Beginner' in con.title:
                    self.jobs.add(con)
            except Exception as e:
                print(e)
    
    def check_queue(self):
        t = datetime.now().timestamp()
        while self.jobs and (con:=min(self.jobs)).timestamp < t + 30:
            self.jobs.remove(con)
            self.send_message(con)
    
    def send_message(self, con: Contest):
        body = {
            'content': f'<@&936589677132124160> あと30分で {con.title} が始まります\n{con.url}'
        }
        requests.post(WEBHOOK, json=body)

    def write_queue(self):
        s = json.dumps(list(map(asdict, sorted(self.jobs))), indent=2)
        Path(QUEUE).write_text(s)

if __name__ == '__main__':
    ac_alert = AtCoderAlert()
    ac_alert.run()