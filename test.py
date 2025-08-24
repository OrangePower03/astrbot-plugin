from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *

# https://github.com/OrangePower03/astrbot-plugin
@register("test", "Charlie", "一个简单测试", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("t")
    async def test(self, event: AstrMessageEvent):
        if event.is_wake:
            yield event.plain_result(event.get_message_outline())

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass
