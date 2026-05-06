# にじさんじ 推しジャンル スケジュール管理ツール

にじさんじ公式サイトから「雑談」「朝配信」などの特定ジャンルの配信を自動抽出し、番組表として表示するシステムです。

## セットアップ手順

### 1. リポジトリの準備

このリポジトリをそのまま自分のGitHubアカウントにフォークまたはコピーします。

### 2. Discord Webhook URLを設定する

1. Discordの通知を送りたいチャンネルを開く
2. チャンネル設定 → 連携サービス → ウェブフックを作成
3. Webhook URLをコピー
4. GitHubリポジトリの **Settings → Secrets and variables → Actions** を開く
5. `DISCORD_WEBHOOK_URL` という名前でシークレットを追加し、URLを貼り付ける

### 3. GitHub Pagesを有効にする

1. GitHubリポジトリの **Settings → Pages** を開く
2. Source: `Deploy from a branch`
3. Branch: `main` / フォルダ: `/docs` を選択して保存

### 4. GitHub Actionsを有効にする

リポジトリの **Actions** タブを開き、ワークフローを有効化します。  
手動で実行する場合は「Run workflow」ボタンから実行できます。

---

## キーワードの変更方法

`config/keywords.json` を直接GitHubの画面で編集します。

```json
{
  "keywords": [
    "雑談",
    "朝配信",
    "歌枠"
  ]
}
```

ファイルを保存（コミット）すると、次回のActionsの定期実行（最大20分後）に反映されます。

---

## ファイル構成

```
├── .github/workflows/fetch.yml   # 20分おきに自動実行
├── config/keywords.json          # キーワード設定（ここを編集）
├── data/streams.json             # 取得したデータ（自動更新）
├── scripts/fetch.py              # データ取得スクリプト
└── docs/index.html               # GitHub Pages フロントエンド
```

---

## APIレスポンスの構造が異なる場合

`scripts/fetch.py` の `filter_streams` 関数内でフィールド名を調整してください。

```python
"liver_name": s.get("liver", {}).get("name", s.get("liver_name", "")),
```

実際のAPIレスポンスのキー名に合わせて `.get("キー名")` の部分を変更します。
