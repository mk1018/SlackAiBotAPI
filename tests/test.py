import os
import json
import time
import hmac
import hashlib
from function.lambda_function import lambda_handler


def test_lambda_handler():
    # Slackからのリクエストをシミュレートするイベントデータを作成
    test_event = {
        "headers": {
            "X-Slack-Request-Timestamp": str(int(time.time())),
            "X-Slack-Signature": "",  # 署名は後で計算します
        },
        "body": json.dumps(
            {
                "event": {
                    "type": "app_mention",
                    "user": "U1234567890",
                    "text": "<@U07MY0SMH6D> ビットコインについて教えてください",
                    "channel": "C1234567890",
                }
            }
        ),
    }

    # 署名を計算してヘッダーに設定
    slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
    request_body = test_event["body"]
    timestamp = test_event["headers"]["X-Slack-Request-Timestamp"]
    sig_basestring = f"v0:{timestamp}:{request_body}".encode("utf-8")
    my_signature = (
        "v0="
        + hmac.new(
            slack_signing_secret.encode("utf-8"), sig_basestring, hashlib.sha256
        ).hexdigest()
    )

    test_event["headers"]["X-Slack-Signature"] = my_signature

    # コンテキストは不要なのでNoneを指定
    context = None

    # Lambda関数を呼び出して結果を取得
    result = lambda_handler(test_event, context)

    # 結果を表示
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 結果の検証
    assert isinstance(result, dict), "結果は辞書型であるべきです。"
    assert "statusCode" in result, "結果には'statusCode'が含まれるべきです。"
    assert result["statusCode"] == 200, "ステータスコードは200であるべきです。"


if __name__ == "__main__":
    test_lambda_handler()
