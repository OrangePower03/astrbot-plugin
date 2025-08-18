from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *

@register("test", "Charlie", "一个简单的测试组件", "1.0.0")
class TestPlugin(Star):

    def __init__(self, context: Context):
        super().__init__(context)
        self.base_url = "http://backend:8080"

    @filter.command("test")
    def test(self, event: AstrMessageEvent):
        event.plain_result("ok")
