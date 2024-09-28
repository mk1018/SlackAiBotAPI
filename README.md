# SlackAiBot

## ryeのインストール for mac
```
curl -sSf https://rye-up.com/get | bash
echo 'source "$HOME/.rye/env"' >> ~/.zshrc
source ~/.zshrc
```

## プロジェクトの環境構築
```
rye sync
```

## .envrcの設定
```
cp .envrc.example .envrc
```

## フォーマット
```
rye run format
```

# セットアップ方法

## Slack側の設定

### アプリの作成
https://api.slack.com/apps?new_app=1

`Create New App` を選択

![alt text](<images/1_CreateNewApp.png>)

`From scratch` を選択

![alt text](<images/2_CreateAnApp.png>)

App Nameとworkspaceを入力

![alt text](<images/3_AppName.png>)

### アプリの設定

アプリが作成できたら `OAuth & Permissions` のページから `Scopes` に以下を設定

- app_mentions:read
- chat:write
- groups:read

![alt text](<images/4_OAuth&Permissions.png>)
![alt text](<images/5_Scopes.png>)

### Workspaceにインストール

`Install to <Workspace名>` でインストール

![alt text](images/6_OAuthTokens.png)

## コード側の設定

二つの環境変数を設定する
- SLACK_BOT_TOKEN
- SLACK_SIGNING_SECRET

#### SLACK_BOT_TOKEN

OAuth & Permissions

![alt text](images/7_BotUserOAuthToken.png)

#### SLACK_SIGNING_SECRET

Basic Information

![alt text](images/8_SigningSecret.png)
