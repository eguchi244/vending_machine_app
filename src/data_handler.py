"""
data_handler: 取引ログの永続化(CSV出力)
役割：イベントをそのまま記録する（計算はしない）
"""

import csv
import json
from datetime import datetime
import os

# ファイルパス
LOG_FILE = "vending_machine_log.csv"

def add_transaction_log(
    log_type: str,
    amount: int,
    item: str = "-",
    change_detail: dict[int, int] | None = None,
    balance_before: int = 0,
    balance_after: int = 0,
    inventory_after: dict[int, int] | None = None,
) -> None:
    """
    ログファイルに取引イベントをCSVに1行追記する

    Args:
        log_type (str): deposit / purchase / refund
        amount (int): 取引で扱った金額（depositは正の値、purchase/refundは負の値を想定)
        item (str): 商品名（該当なしは"-"）
        change_detail (dict[int, int] | None): お釣り内訳
        balance_before (int): 処理前の金庫総額
        balance_after (int): 処理後の金庫総額
        inventory_after (dict[int, int] | None): 処理後の金庫各金種の枚数
    """

    # お釣り内訳と処理後の金種枚数を「JSON化 + None対策 + 文字化け対策」する
    detail_str = json.dumps(
        change_detail if change_detail else {},
        ensure_ascii=False
    )
    inventory_str = json.dumps(
        inventory_after if inventory_after else {},
        ensure_ascii=False
    )

    # レコード用の配列を作成
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        log_type,
        item,
        amount,
        detail_str,
        balance_before,
        balance_after,
        inventory_str,
    ]
    
    # ログファイル存在確認
    file_exists = os.path.isfile(LOG_FILE)

    # 取引イベントをCSVに1行追記する
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # ファイルの新規作成時にヘッダーを付与する
        if not file_exists:
            writer.writerow([
                "datetime",
                "log_type",
                "item",
                "amount",
                "change_detail",
                "balance_before",
                "balance_after",
                "inventory_after",
            ])
        
        # レコードに取引イベントを書き込む
        writer.writerow(row)