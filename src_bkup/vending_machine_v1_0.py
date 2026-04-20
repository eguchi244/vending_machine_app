"""
自販機アプリ

このアプリはCLIの自販機シミュレーターのロジックを制御します。
"""
# main関数
def main():

    #商品一覧の価格設定
    DRINK_MENU = {"Water": 100, "Tea": 120, "Cola": 150, "Monster": 210}

    # 投入金額入力を促すメッセージ
    money_input = input("お金を投入してください。\n")

    # 金額入力の数値判定で分岐する
    if not money_input.isdigit(): 
        print("金額を入力さてれいません。金額を入力して再度購入してください。")
    else:
        # 商品一覧を表示
        print("\n--- 商品ラインナップ ---")
        for name, price in DRINK_MENU.items():
            print(f"{name}:{price}円")
        print("------------------------")

        # 商品を選択
        selected_item = input("購入する商品を選んでください: ")

        # try..except(商品取り出しでリストにない場合)
        try:
            #選択した商品の価格を格納
            price = DRINK_MENU[selected_item]
        # 商品リストにない場合
        except(KeyError): 
            print("%s は商品にありません。" %selected_item)
        # 商品リストにある場合
        else:
            # お釣り計算
            change = int(money_input) - price

            #金額が足りている場合
            if change > 0: 
                print(f"\n{selected_item} を選択しました。")
                print(f"お釣りは {change} 円です。")
            #金額が足りてない場合
            else:
                print("\n金額が不足しています。")

# main関数呼び出し
if __name__ == "__main__":
    main()
