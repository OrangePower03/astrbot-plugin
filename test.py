# https://github.com/OrangePower03/astrbot-plugin
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *


@register("test", "Charlie", "一个简单的测试插件", "1.0.0")
class TestPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("t")
    async def test(self, event: AstrMessageEvent):
        if event.is_wake:
            yield event.plain_result(event.get_message_outline())