"""
CashManager: 自販機の金庫管理クラス
役割: 現金の在庫管理、お釣り計算アルゴリズムの実行、在庫の増減処理
"""

class CashManager:
    # 投入上限設定（安全装置）
    MAX_DEPOSIT_LIMITS = {
        10000: 5, 5000: 5, 1000: 10, 500: 20, 100: 20,50: 20, 10: 20
    }

    def __init__(self, inventory: dict[int, int], deposit: dict[int, int]) -> None:
        """
        金庫を初期化し、計算用に金種をソートして保持する
        
        Args:
            inventory (dict[int, int]): 金庫の金種(int)と枚数(int)のペア
            deposit (dict[int, int]): 投入金額の金種(int)と枚数(int)のペア
        """
        self.inventory = inventory
        # 貪欲法（大きい順に試行）のため、金種をあらかじめ降順でリスト化しておく
        self._bills_desc = sorted(self.inventory.keys(), reverse=True)
        # 現在の各金種の投入枚数を管理
        self.current_bills_deposit = deposit

    def deposit(self, bill_type: int) -> None:
        """
        投入された現金を金庫の在庫に反映する
        
        Args:
            bill_type (int): 投入された金種（例: 1000）
        Raises:
            ValueError: 取り扱い対象外の金種が渡された場合,
                        投入制限を超過した金種が渡された場合
        """
        # 金種判定
        if bill_type not in self.inventory:
            raise ValueError(f"未登録の金種です: {bill_type}")
        
        # 投入枚数制限の判定
        limit = self.MAX_DEPOSIT_LIMITS.get(bill_type, 0)
        if self.current_bills_deposit[bill_type] >= limit:
            raise ValueError(f"{bill_type}円の投入枚数が制限（{limit}枚）に達しました。")

        # 在庫に加算
        self.inventory[bill_type] += 1
        # 投入枚数に加算
        self.current_bills_deposit[bill_type] += 1

    def reset_bills_deposit(self) -> None:
        """
        現在の各金種の投入枚数をリセットするメソッド
        """
        # self.current_bills_deposit = {bill: 0 for bill in self._bills_desc}
        for bill in self.current_bills_deposit:
            self.current_bills_deposit[bill] = 0

    def calc_change(self, amount: int) -> dict[int, int]:
        """
        指定された金額に対し、現在の在庫から払い出し可能な内訳を算出する
        
        Algorithm:
            高額紙幣から順に、在庫の許す限りお釣りに割り当てる。(貪欲法)

        Returns:
            change_detail (dict[int, int]): 
                成功時：払い出すべき各金種の枚数（全金種分を網羅）
                失敗時：空の辞書（在庫不足などで1円単位まで払いきれない場合）
        """
        # お釣りなし（0円）の場合は、全金種0枚の内訳を返す
        if amount == 0:
            return {bill: 0 for bill in self._bills_desc}

        # お釣りの内訳の初期化
        change_detail = {bill: 0 for bill in self._bills_desc}
        remaining_amount = amount

        # お釣りの内訳への各金種への割り当て(貪欲法)
        for bill in self._bills_desc:
            # その金種で理論上何枚払えるか算出
            count_needed = remaining_amount // bill
            # 理論上の枚数と、実際の在庫枚数の少ない方を採用
            count_to_give = min(count_needed, self.inventory[bill])
            # 各金種に応じた釣銭の枚数を格納
            change_detail[bill] = count_to_give
            # お釣りの残額を減算
            remaining_amount -= bill * count_to_give

        # 最終的に1円も余さず払いきれたかチェック
        if remaining_amount == 0:
            return change_detail
        else:
            # 端数が残る、あるいは在庫不足で払いきれないケース
            return {}

    def update_inventory(self, change_detail: dict[int, int]) -> None:
        """
        お釣りとして算出した枚数を実際に金庫から差し引く
        
        Args:
            change_detail (dict[int, int]): calc_change() で得られた枚数内訳
        """
        for bill, count in change_detail.items():
            # 念のため、実行直前に在庫不足が起きていないか確認
            if self.inventory[bill] < count:
                raise ValueError(f"在庫不整合: {bill}円が不足しています")
            self.inventory[bill] -= count

    @property
    def total_inventory_value(self) -> int:
        """金庫内の現金の時価総額"""
        return sum(bill * count for bill, count in self.inventory.items())


# =========================
# テストシナリオ
# =========================
# テスト用の初期データ準備
def get_test_data():
    inventory = {10000: 10, 5000: 10, 1000: 10, 500: 10, 100: 10, 50: 10, 10: 10}
    # 投入制限チェック用の空カウンタ
    deposit = {k: 0 for k in inventory.keys()}
    return inventory, deposit

def test_calc_change_success():
    """正常系: 投入とお釣り計算、在庫更新が正しく連動することを確認"""
    # テスト用の初期データ
    inventory, deposit = get_test_data()
    cash_manager = CashManager(inventory, deposit)

    # 1000円投入（在庫が増える）
    cash_manager.deposit(1000)

    # 880円のお釣りを要求(120円商品購入を想定)
    # 想定: 500x1, 100x3, 50x1, 10x3
    change = cash_manager.calc_change(880)
    print(f"お釣り内訳(880円): {change}")

    # 在庫を反映
    cash_manager.update_inventory(change)
    print(f"更新後の在庫: {cash_manager.inventory}")
    
    # 期待値検証（ロジックにミスがないか総額でチェック）
    # 初期(166,600) + 投入(1,000) - 払出(880) = 166,720
    assert cash_manager.total_inventory_value == 166720


def test_calc_change_stock_shortage():
    """異常系: 在庫（100円玉以下）が足りない場合に空の辞書が返ることを確認"""
    # 100円以下が0枚の金庫
    inventory = {10000: 10, 5000: 10, 1000: 10, 500: 0, 100: 0, 50: 0, 10: 0}
    deposit = {k: 0 for k in inventory.keys()}

    cash_manager = CashManager(inventory, deposit)

    # 200円のお釣りは払えないはず
    change = cash_manager.calc_change(200)
    assert change == {}
    print("在庫不足時のエラーハンドリング確認: OK")

if __name__ == "__main__":
    test_calc_change_success()
    test_calc_change_stock_shortage()