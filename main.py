import re

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

    @filter.command("说明书")
    async def specification(self, event: AstrMessageEvent):
        param = event.get_message_str().removeprefix("说明书").strip()
        res: str
        if len(param) == 0:
            res = """
                /说明书 [指令功能]
                指令功能: 图片;聊天记录;题库
            """
        elif param == "图片":
            res = pic_specification
        elif param == "聊天记录":
            res = record_specification
        elif param == "题库":
            res = "暂未开放功能点，等待答题活动开启"
        else:
            res = "指令功能不存在"
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
            return
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
            }
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
            "sender": event.get_sender_id(),
            "message": event.message_str
        }
        # logger.info(body)
        res = requests.post(url=url, json=body)
        yield event.plain_result(res.text)

    ### 题库
    @filter.command("题库")
    async def ask_question_library(self, event: AstrMessageEvent):
        question = event.get_message_str().removeprefix("题库").strip()
        if len(question) == 0:
            yield event.plain_result("请输入题目")
            return
        yield event.plain_result("正在调用，ai需要深度思考，请耐心等待，一分钟内不响应再重新问")
        url = self.base_url + f"/question/ask/{question}"
        res = requests.post(url=url)
        yield event.plain_result(res.text)

    @filter.command("1")
    async def add_question(self, event: AstrMessageEvent):
        messages: [BaseMessageComponent] = event.get_messages()
        for message in messages:
            if isinstance(message, Reply):
                logger.info(f"引用输出的消息内容：{message.message_str}")
                pattern = r'\{("答案":"[^"]*","答案来源":"[^"]*","问题":"[^"]*")\}'
                match = re.search(pattern, message.message_str)
                if not match:
                    yield event.plain_result("你引用的内容格式不正确，叫可乐来修")
                    logger.error("正则无法匹配出指定的字符")
                    return
                ai_res = "{" + match.group(1) + "}"
                try:
                    data: dict = json.loads(ai_res)
                    body = {
                        "question": data["问题"],
                        "answer": data["答案"],
                        "source": data["答案来源"]
                    }
                    if body["source"] == "题库":
                        yield event.plain_result("题库中已存在，无需添加")
                        return
                    url = self.base_url + "/question/add"
                    res = requests.post(url=url, json=body)
                    if res.ok:
                        yield event.plain_result("成功添加")
                except json.JSONDecodeError as e:
                    yield event.plain_result("你引用的内容格式不正确，叫可乐来修")
                    logger.error(e.msg)
                break

        else:
            yield event.plain_result("请引用了题目才能成功添加")

    @filter.command("test")
    async def test(self, event: AstrMessageEvent):
        if event.is_wake:
            yield event.plain_result(event.get_message_outline())

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
        pass


pic_specification = """
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

record_specification = """
聊天记录默认是会自动收取所有文本内容
消息发出后会自动将聊天内容、QQ号传输给到数据库里存者

当你需要找聊天记录或者想问一些问题时，可以调用指令
/问 [问题]
问题不能为空，然后就会先去查找数据库，查完再上下找几条记录
一块传给ai，最后调用ai返回
主要用途是查一些聊天记录，杜绝拿来攻击群友
"""

question_specification = """
这个功能是专门用于游戏中答题活动提高各位答题率而准备的
题库中存储了以往的题目，不止止是ai
你描述的问题越详细，ai总结到题库后输出的越准确
如果你输出的不够详细，可能会导致题库中存在多个类似的题目
最后ai会返回最相近的所有答案，以分号分割开，根据题目选项选择

具体用法：
/题库 [问题]

解释：问题不能为空，最后会输出三个东西
{"问题": "", "答案": "", "答案来源": ""}
注意，如果答案来源是AI且答对了的，代表题库中并不存在这个题目
麻烦各位调用下面的指令来追加这个题目

[引用机器人返回的内容]
/1

解释：将机器人输出引用并输出指令 /1 就好，非常方便
"""