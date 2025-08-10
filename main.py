import requests

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *


@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):

    def __init__(self, context: Context):
        super().__init__(context)
        self.base_url = "http://backend:8080"

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        pass

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令"""  # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str  # 用户发的纯文本消息字符串
        message_chain = event.get_messages()  # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")  # 发送一条纯文本消息

    @filter.command("test")
    async def test(self, event: AstrMessageEvent):
        pass







    # @filter.command("send_image")
    # async def send_image(self, event: AstrMessageEvent):
    #     yield event.image_result("https://cq-note.oss-cn-hangzhou.aliyuncs.com/20250425232807.png")

    @filter.command("添加词条")
    async def addDict(self, event: AstrMessageEvent):
        url = self.base_url + "/image/addDict"
        body = {
            "dict": event.message_str.removeprefix("添加词条").strip()
        }
        res = requests.post(url=url, json=body)
        yield event.plain_result(res.text)


    @filter.command("添加图片")
    async def addPic(self, event: AstrMessageEvent):
        chain = event.get_messages()
        if len(chain) <= 1:
            yield event.plain_result("请引用一张图片")
        elif len(chain) > 2:
            yield event.plain_result("消息太多了,只能引用图片再输出文字添加")
        else:
            if isinstance(chain[0], Reply):
                chain_chain = chain[0].chain
                if len(chain_chain) == 1 and isinstance(chain_chain[0], Image):
                    dict = event.message_str.removeprefix("添加图片").strip()
                    image: Image = chain_chain[0]
                    if len(dict) == 0:
                        yield event.plain_result("请在添加图片后加上你要添加到的词条,如 添加图片 可乐")
                        return

                    yield event.plain_result(f"词条:{dict},引用消息图片url:{image.url},图片file:{image.file},图片file_unique:{image.file_unique},图片path:{image.path}")
                else:
                    yield event.plain_result("引用数据太多或者引用数据不是图片")
                # url = self.base_url + "/image/addPic"
                # body = {
                #     "dict": dict,
                #     "image": image
                # }
                # res = requests.post(url=url, json=body)
                # if res.text == "ok":
                #     yield event.plain_result("添加成功")
                # elif res.text == "词条不存在":
                #     yield event.plain_result(f"词条{dict}不存在,请先添加词条")
                # else:
                #     yield event.plain_result("添加失败,服务器异常")
            else:
                yield event.plain_result("第一条数据必须是引用")
                return


    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass
