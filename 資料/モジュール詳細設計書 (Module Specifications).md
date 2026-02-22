モジュール詳細設計書 

バックエンド（FastAPI）の主要モジュールのインターフェース（入出力）および内部処理ロジックを定義します。

1. APIエンドポイント (Routers)

1.1 GET /api/v1/events/{event_id}/summary

概要: 指定されたイベントの候補日程一覧、全ユーザーの回答マトリクス、およびレコメンド（おすすめ日程）の集計結果を取得する。

リクエストパラメータ:

event_id (Path): 対象のイベントID

レスポンス (200 OK):

{
  "event": { "id": 1, "title": "合宿調整" },
  "recommended_dates": [
    { "date_id": 3, "date": "2026-03-15", "score": 8, "available_count": 4, "adjustable_count": 0 }
  ],
  "matrix": [
    {
      "user_id": "uuid-xxxx",
      "username": "田中",
      "answers": [
        { "date_id": 1, "status": 2, "comment": "" },
        { "date_id": 2, "status": 1, "comment": "19時以降なら" }
      ]
    }
  ]
}


内部処理 (Service層呼び出し): SummaryService.generate_event_summary(event_id) を呼び出す。

1.2 POST /api/v1/answers

概要: ユーザーが回答を登録・更新する。

リクエストヘッダー:

X-User-ID: フロントエンドが生成したUUID

リクエストボディ (JSON):

{
  "username": "田中",
  "answers": [
    { "event_date_id": 1, "status": 2, "comment": "" },
    { "event_date_id": 2, "status": 1, "comment": "遅れて参加" }
  ]
}


レスポンス (200 OK): 成功メッセージ。

エラー (422): Pydanticによるバリデーションエラー（ステータスが0,1,2以外など）。

2. サービスモジュール (Business Logic)

2.1 SummaryService (集計・レコメンドアルゴリズム)

関数名: calculate_date_scores(answers_data)

処理ロジック:
各候補日程について、全ユーザーの回答ステータスを集計し、以下のスコアを算出する。
Score = (Status=2の人数 * 2) + (Status=1の人数 * 1)

ソートアルゴリズム:
スコアの降順でソート。スコアが同値の場合は、参加可能(Status=2)の人数が多い順、さらに同値なら日付の早い順とする。計算量は日程数$M$、ユーザー数$N$に対し $O(M \log M + NM)$ となる（$N, M$が小さいためメモリ上で処理）。

3. データアクセスモジュール (CRUD)

3.1 crud_answer.py

関数名: upsert_user_answers(db: Session, user_id: UUID, answers: List[AnswerCreate])

処理ロジック:
SQLAlchemyを使用し、渡されたリスト内の回答を1つのトランザクション内で処理する。
すでにデータベースに user_id と event_date_id の組み合わせが存在する場合は status と comment をUPDATEし、存在しない場合はINSERTする。N+1問題を避けるため、一括操作（Bulk operation）を推奨する。
