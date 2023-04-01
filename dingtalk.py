import datetime
import requests
import json
from dateutil import parser
from flask import Flask, request
from gevent.pywsgi import WSGIServer


def time_zone_conversion(utctime):
    """
    :param utctime: UTC时间格式
    :return: 返回正确时区，+8
    """
    format_time = parser.parse(utctime).strftime('%Y-%m-%dT%H:%M:%SZ')
    time_format = datetime.datetime.strptime(format_time, '%Y-%m-%dT%H:%M:%SZ')
    return str(time_format + datetime.timedelta(hours=8))


def sendDingMes(msg):
    """
    实现告警信息通知钉钉
    :param msg:钉钉要求的数据格式发送
    :return:
    """
    # 填写钉钉机器人的Webhook
    baseUrl = "自定义机器人webhook"
    # 设置头
    HEADERS = {
        "Content-Type": "application/json ;charset=utf-8"
    }
    msgBody = json.dumps(msg)
    result = requests.post(url=baseUrl, headers=HEADERS, data=msgBody)
    print(f"执行结果: {result.text}")


app = Flask("dingTalk_api")


@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        prometheus_data = json.loads(request.data)
        # 时区转换
        for k, v in prometheus_data.items():
            if k == 'alerts':
                for items in v:
                    if items['status'] == 'firing':
                        items['startsAt'] = time_zone_conversion(items['startsAt'])
                        msg = {
                            "msgtype": "markdown",
                            "markdown": {
                                "title": "Prometheus告警信息",
                                "text": f"#### 监控指标 {items['labels']['alertname']}\n" + f"> 监控描述信息 {items['annotations']['description']}\n\n" + f"> ##### 告警时间 {items['startsAt']}\n"
                            },
                            "at": {
                                "atMobiles": [
                                    "16620101812",
                                ],
                                # @所有人，设置为true时atMobiles失效
                                "isAtAll": "false"
                            }
                        }
                    else:
                        items['startsAt'] = time_zone_conversion(items['startsAt'])
                        items['endsAt'] = time_zone_conversion(items['endsAt'])
                        msg = {
                            "msgtype": "markdown",
                            "markdown": {
                                "title": "Prometheus告警信息",
                                "text": f"#### 监控指标 {items['labels']['alertname']}\n" +
                                        f"> 监控描述信息 {items['annotations']['description']}\n\n" +
                                        f"> ##### 告警时间 {items['startsAt']}\n"
                                        f"> ##### 恢复时间 {items['endsAt']}\n"
                            },
                            "at": {
                                "atMobiles": [
                                    "16620101812",
                                ],
                                # @所有人，设置为true时atMobiles失效
                                "isAtAll": "false"
                            }
                        }
                    sendDingMes(msg)
    except Exception as e:
        raise e
    return "test"


if __name__ == "__main__":
    WSGIServer((('0.0.0.0'), 5000), app).serve_forever()
