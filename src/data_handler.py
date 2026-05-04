"""
data_handler: 取引ログの永続化(CSV出力)
役割：イベントをそのまま記録する（計算はしない）
"""

import csv
import json
from datetime import datetime
import os

# ファイルパス
LOG_FILE = "../log/vending_machine_log.csv"

def add_transaction_log(
    log_type: str,
    amount: int,
    item: str = "-",
    change_detail: dict[int, int] | None = None,
    balance_before: int = 0,
    balance_after: int = 0,
    inventory_after: dict[int, int] | None = None,
    item_stock_after: dict[str, int] | None = None,
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
        item_stock_after (dict[str, int] | None): 補充後の各商品の在庫数

    """

    # お釣り内訳を「JSON化 + None対策 + 文字化け対策」する
    detail_str = json.dumps(
        change_detail if change_detail else {},
        ensure_ascii=False
    )
    # 金種枚数を「JSON化 + None対策 + 文字化け対策」する
    inventory_str = json.dumps(
        inventory_after if inventory_after else {},
        ensure_ascii=False
    )

    # 在庫商品を「JSON化 + None対策 + 文字化け対策」する
    item_stock_str = json.dumps(
        item_stock_after if item_stock_after else {},
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
        item_stock_str,
    ]
    
    # ログファイル存在確認
    file_exists = os.path.isfile(LOG_FILE)

    # 取引イベントをCSVに1行追記する
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8-sig") as f:
        # writerオブジェクトを作成
        writer = csv.writer(f)

        # ファイルの新規作成時にヘッダーを付与する
        if not file_exists:
            # ヘッダーを書き込む
            writer.writerow([
                "datetime",
                "log_type",
                "item",
                "amount",
                "change_detail",
                "balance_before",
                "balance_after",
                "inventory_after",
                "item_stock_after",
            ])
        
        # レコードに取引イベントを書き込む
        writer.writerow(row)

def get_latest_inventory_from_csv():
    """CSVの最終行から在庫情報を読み取る"""
    # ログファイル存在確認
    if not os.path.isfile(LOG_FILE):
        # 存在しない場合は処理を終了
        return None, None

    try:
        # CSVの最終行から在庫情報を読み取る
        with open(LOG_FILE, mode="r", encoding="utf-8-sig") as f:
            # CSV読み込む
            reader = list(csv.DictReader(f))

            # ヘッダーのみ、または空の場合は処理を終了
            if not reader:
                return None, None
            
            # ヘッダー最終行を取得
            last_row = reader[-1]

            # 列名で直接指定して取得(JSON文字列を辞書に復元)
            raw_inventory = json.loads(last_row["inventory_after"])
            item_stock = json.loads(last_row["item_stock_after"])

            # NOTE JSONの仕様でキーが文字列 ("1000") になっているため数値 (1000) に変換
            inventory = {int(k): v for k, v in raw_inventory.items()}

            # 処理後の各金種枚数と在庫数を返す
            return inventory, item_stock
    
    except Exception as e:
        raise RuntimeError(f"データ読み込みエラー: {e}")