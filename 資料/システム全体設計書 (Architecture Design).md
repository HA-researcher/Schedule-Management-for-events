システム全体設計書 

1. システムアーキテクチャ概要

本システムは、保守性と拡張性を重視し、フロントエンドとバックエンドを疎結合に保つRESTful APIアーキテクチャを採用する。

Frontend: React (SPA)。UIの構築と状態管理（State）を担当。APIサーバーへ非同期通信（fetch/axios）を行う。

Backend: FastAPI (Python 3.10+)。APIの提供、リクエストのバリデーション、ビジネスロジック（集計アルゴリズム）の実行、DBとの連携を担当。

Database: PostgreSQL。データの永続化。ORMを介して操作。

2. インフラ・デプロイメント構成

無料枠を活用しつつ、実運用に耐えうる構成とする。

graph LR
    User([Browser/Mobile]) -->|HTTPS| Vercel[Frontend: Vercel]
    User -->|API Request (CORS)| RenderWeb[Backend: Render Web Service]
    Vercel -.->|Deploy| GitHub[(GitHub Repo)]
    RenderWeb -.->|Deploy| GitHub
    RenderWeb -->|SQL| RenderDB[(PostgreSQL on Render)]


CORS (Cross-Origin Resource Sharing):
フロントエンド(Vercelのドメイン)とバックエンド(Renderのドメイン)が異なるため、FastAPI側で CORSMiddleware を設定し、Vercelのドメインからの通信のみを許可する（セキュリティ確保）。

3. エラーハンドリング方針

APIからのエラーレスポンスは、フロントエンドが扱いやすいように一貫したフォーマットに統一する。

エラーレスポンス共通フォーマット:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "ステータスは 0, 1, 2 のいずれかを指定してください。",
    "details": [ ... ]
  }
}


400 Bad Request: クライアント起因のエラー（不正なUUIDなど）。

404 Not Found: 指定されたリソース（イベント等）が存在しない。

422 Unprocessable Entity: リクエストの形式は正しいが、バリデーション（型や値の範囲）に違反している（FastAPI標準）。

500 Internal Server Error: DB接続失敗など、サーバー側の予期せぬエラー。

4. ディレクトリ構造の設計思想

クリーンアーキテクチャの思想を取り入れ、以下のように責務を分割する。

api/: エンドポイントの定義。HTTPリクエストの受付とレスポンスの返却に特化。

schemas/: Pydanticを用いたAPIデータの型定義。入力値の自動バリデーションを行う。

services/: アルゴリズム（AtCoderのコードに相当する部分）や、DB操作を組み合わせたビジネスロジック。

crud/: データベースへの直接的なクエリ（SQLAlchemy）をカプセル化。ルーターから直接SQLを書くことを禁止する。

models/: データベースのテーブル定義（Entity）。
