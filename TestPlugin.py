from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *


@register("test", "Charlie", "一个简单的测试插件", "1.0.0")
class TestPlugin(Star):
    @filter.command("test")
    async def test(self, event: AstrMessageEvent):
        if event.is_wake:
            yield event.plain_result(event.get_message_outline())