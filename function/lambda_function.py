import os
import json
import logging
import hmac
import hashlib
import time
from slack_sdk import WebClient
from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# クライアントの初期化
slack_client = WebClient(token=SLACK_BOT_TOKEN)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

system_prompt = """
ユーザーからの質問に簡潔に回答してください。

## 条件
- マークダウン形式で返答してください。
- 「長文で」「詳細に」など詳細を求められた場合にも長文で回答してください。
"""


def verify_slack_request(headers, body):
    timestamp = headers.get("X-Slack-Request-Timestamp")
    signature = headers.get("X-Slack-Signature")

    # リクエストが古すぎる場合は無視（5分以上前）
    if abs(time.time() - int(timestamp)) > 60 * 5:
        logger.warning("リクエストのタイムスタンプが古すぎます。")
        return False

    # 署名シークレットを使用して署名を生成
    sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
    my_signature = (
        "v0="
        + hmac.new(
            SLACK_SIGNING_SECRET.encode("utf-8"), sig_basestring, hashlib.sha256
        ).hexdigest()
    )

    # Slackからの署名と比較
    if not hmac.compare_digest(my_signature, signature):
        logger.warning("リクエストの署名が無効です。")
        return False

    return True


def lambda_handler(event, context):
    # API Gatewayからのリクエストを取得
    headers = event.get("headers", {})
    body = event.get("body", "")

    # リクエストの検証
    if not verify_slack_request(headers, body):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid request signature"}),
        }

    data = json.loads(body)

    # URL検証用のチャレンジ応答
    if "challenge" in data:
        logger.info(f"Slackチャレンジ応答")
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/plain"},
            "body": data["challenge"],
        }

    # リトライヘッダーの確認
    # slackは3秒以内にレスポンスが返ってこないとリトライを実行する。それを無視するためのもの。
    if "X-Slack-Retry-Num" in headers:
        logger.warning(
            f"リトライリクエストを無視します。リトライ番号: {headers['X-Slack-Retry-Num']}"
        )
        return {"statusCode": 200, "body": json.dumps({"status": "ignored"})}

    # イベントの処理
    if "event" not in data:
        logger.error(f"bodyにeventがありません。")
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid request"}),
        }

    event_data = data["event"]

    # メンションのみ
    if event_data.get("type") == "app_mention":
        text = event_data.get("text")
        channel = event_data.get("channel")

        # ボットのユーザーIDを取得
        auth_response = slack_client.auth_test()
        bot_user_id = auth_response["user_id"]

        # メンションは不要なので除去
        clean_text = text.replace(f"<@{bot_user_id}>", "").strip()

        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {"role": "user", "content": clean_text},
                ],
            )
            reply = response.choices[0].message.content

            # Slackにメッセージを送信
            slack_response = slack_client.chat_postMessage(channel=channel, text=reply)

            logger.info(f"Slack API response: {slack_response}")
        except Exception as e:
            logger.error(f"レスポンス生成中にエラーが発生しました: {e}")
            slack_client.chat_postMessage(
                channel=channel,
                text="リクエストを処理できませんでした。",
            )

    return {"statusCode": 200, "body": json.dumps({"status": "success"})}
