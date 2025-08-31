# https://github.com/OrangePower03/astrbot-plugin
import re
import json

text = '[引用消息(牛马:  @orz*╰╮o(￣▽￣///)(1697081049) {"答案":"破釜沉舟","答案来源":"词库","问题":"题库 项羽"})]'

# 方法1：直接匹配固定的键名模式
pattern = r'\{("答案":"[^"]*","答案来源":"[^"]*","问题":"[^"]*")\}'
match = re.search(pattern, text)

if match:
    json_str = '{' + match.group(1) + '}'
    data = json.loads(json_str)
    print(data)
    # 输出: {'答案': '破釜沉舟', '答案来源': '词库', '问题': '题库 项羽'}
else:
    print("未找到匹配的JSON")