import requests

from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import *
from datetime import datetime
import pytz


@register("image", "Charlie", "一个简单的图片添加插件", "1.0.0")
class MyPlugin(Star):

    def __init__(self, context: Context):
        super().__init__(context)
        self.base_url = "http://backend:8080"

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        pass

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    # @filter.command("helloworld")
    # async def helloworld(self, event: AstrMessageEvent):
    #     """这是一个 hello world 指令"""  # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
    #     user_name = event.get_sender_name()
    #     message_str = event.message_str  # 用户发的纯文本消息字符串
    #     message_chain = event.get_messages()  # 用户所发的消息的消息链 # from astrbot.api.message_components import *
    #     logger.info(message_chain)
    #     yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!")  # 发送一条纯文本消息

    @filter.command("说明书")
    async def specification(self, event: AstrMessageEvent):
        res = f"""
            首先如果不存在词条,需要先执行以下指令
            /添加词条 [词条名]
            注意:词条名前必须有空格隔开
            
            然后就可以添加图片了,执行以下指令
            [引用图片]
            /添加图片 [词条名]
            
            注意:必须先引用了才能输入添加图片指令
            
            最后就可以获取随机一张图片了,执行以下指令
            /来只 [词条名]
        """
        yield event.plain_result(res)

    ### 图片
    @filter.command("添加词条")
    async def addDict(self, event: AstrMessageEvent):
        url = self.base_url + "/image/addDict"
        dict = event.message_str.removeprefix("添加词条").strip()
        if len(dict) == 0:
            yield event.plain_result("请在添加图片后加上你要添加到的词条,如 添加图片 可乐")
            return
        body = {
            "dict": dict
        }
        res = requests.post(url=url, json=body)
        yield event.plain_result(res.text)

    @filter.command("添加图片")
    async def addPic(self, event: AstrMessageEvent):
        chain = event.get_messages()
        if len(chain) <= 1:
            yield event.plain_result("请引用一张图片并在下面输出 /添加图片 [词条]")
        else:
            if isinstance(chain[0], Reply):
                chain_chain: [BaseMessageComponent] = chain[0].chain

                for c in chain_chain:
                    if isinstance(c, Image):
                        dict = event.message_str.removeprefix("添加图片").strip()
                        image: Image = c
                        if len(dict) == 0:
                            yield event.plain_result("请在添加图片后加上你要添加到的词条,如 /添加图片 可乐")
                            return
                        logger.info(f"添加图片{dict}")
                        url = self.base_url + "/image/addPic"
                        body = {
                            "dict": dict,
                            "url": image.url,
                            "fileName": image.file
                        }
                        res = requests.post(url=url, json=body)
                        if res.text == "ok":
                            yield event.plain_result("添加成功")
                        else:
                            yield event.plain_result(f"添加失败,服务器错误码:{res.text}")
            else:
                yield event.plain_result("第一条数据必须是引用")

    @filter.command("来只")
    async def send_image(self, event: AstrMessageEvent):
        dict = event.message_str.removeprefix("来只").strip()
        url = self.base_url + f"/image/getRandomPic/{dict}"
        res = requests.post(url=url, json={})
        logger.info(f"接收到返回的链接或错误,返回值为{res.text}")
        if res.text.startswith("http"):
            yield event.image_result(res.text)
        else:
            yield event.plain_result(f"出现错误,错误信息:{res.text}")

    @filter.command("展示词条")
    async def show_dict(self, event: AstrMessageEvent):
        url = self.base_url + f"/image/showDict"
        res = requests.post(url=url)
        if res.status_code == 200:
            yield event.plain_result(res.text)
        logger.error(f"展示词条时服务器错误,错误码:{res.json()}")
        yield event.plain_result("服务器错误")

    ### 聊天记录知识库
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def all_msg(self, event: AstrMessageEvent):
        message = event.message_str.strip()
        if event.get_message_outline().count("/") != 0:
            logger.info(f"{event.get_message_outline()}:为指令语句,不做记录")
            return
        if message != "":
            if "317832838" != event.get_group_id():
                logger.info("不是岛群,仅做测试用")
                return
            tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(tz)
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
            url = self.base_url + "/record/add"
            body = {
                "sendDate": formatted_time,
                "sender": event.get_sender_id(),
                "message": event.message_str,
                # "groupId": event.get_group_id()
            }
            # event.get_group()
            requests.post(url=url, json=body)
            logger.info("聊天记录添加成功")

    @filter.command("问")
    async def ask(self, event: AstrMessageEvent):
        yield event.plain_result("正在调用ai,需要一定的时间,请耐心等待")
        tz = pytz.timezone('Asia/Shanghai')
        now = datetime.now(tz)
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        url = self.base_url + "/record/ask"
        body = {
            "sendDate": formatted_time,
            "sender": event.get_sender_name(),
            "message": event.message_str
        }
        # logger.info(body)
        res = requests.post(url=url, json=body)
        yield event.plain_result(res.text)

    @filter.command("test")
    async def test(self, event: AstrMessageEvent):
        if event.is_wake:
            yield event.plain_result(event.get_message_outline())

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass
