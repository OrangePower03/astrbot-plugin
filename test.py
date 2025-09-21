"""
https://github.com/OrangePower03/astrbot-plugin
"""

import threading
import time
import requests
import json
import astrbot.api.message_components as comp

from astrbot import logger
from astrbot.core.message.message_event_result import MessageChain
from astrbot.core.platform import AstrMessageEvent


class TimedTask:
    def __init__(self, base_url: str, events: dict[str, AstrMessageEvent]):
        self.base_url = base_url
        self.interval = 60
        self.events: dict[str, AstrMessageEvent] = events
        threading.Thread(
            target=self.task,
            # args=(interval_seconds, task_name),
            name=f"Scheduler-task",
            daemon=True  # 设置为守护线程，主程序退出时自动结束
        ).start()

    def task(self):
        while True:
            res = requests.post(url=self.base_url + "/task/get")
            if res.ok:
                body = res.text
                if "pass" != body:
                    d: dict = json.loads(body)
                    qq: [str] = d.get("qq")
                    group_id: str = d["groupId"]
                    text = d["text"]
                    event: AstrMessageEvent = self.events.get(group_id)
                    if event is None:
                        logger.error("发送消息时找不到群聊对应的消息中介")
                    else:
                        chain = []
                        if qq is not None:
                            for i in qq:
                                chain.append(comp.At(qq=i))
                        chain.append(comp.Plain(text=text))
                        yield event.send(MessageChain(chain=chain))

            time.sleep(self.interval)


if __name__ == '__main__':
    d = {}
    print(d.get("a"))
