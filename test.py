# https://github.com/OrangePower03/astrbot-plugin
import json

if __name__ == '__main__':
    json_str = """
    {
        "答案": "test",
        "答案来源": "1.0.0",
        "问题": "test plugin"
    }
    """
    print(json.loads(json_str))
