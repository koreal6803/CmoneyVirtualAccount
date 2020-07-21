# CMoney Stock Paper Trading API
### 為什麼要用 Paper Trading
Paper Trading 可以幫助我們更理解市場上投資的真實狀況，
顯示我們「假如」持有某種資產組合的報酬率，
我們可以自行設定投資金額，例如100萬，並且測試看看，自己精心研發的策略有沒有用

### 為什麼不用回測就好了？
簡單講，大部分寫Python的人，回測框架要達到非常嚴謹，是非常困難的，
所以通常我們都「大概測一測」，比較少考慮的部分有：
1. 胃納量（有些股票根本沒成交量，怎麼可能買很多張？）
2. 不小心使用到未來數據（財報、月營收）
3. 摩擦成本（手續費、證交稅）
4. 忘記把已下市股票給納入回測中
5. 太多了...以後再整理給大家

除了更精密的模擬外，Paper Trading還能夠

### 幫助投資人檢視策略的「微觀效果」
Paper Trading 可以讓你對於投資更有感覺，回測只是看長年下來的獲利績效，
雖然你可能覺得長期績效很好，但是這是個宏觀角度（好幾年），也就是最後得到的總報酬率，
然而我們真正投資的時候，是深處於微觀的世界（每天），會覺得每天的起伏都很劇烈！
有時候會讓你疑神疑鬼，想要調整策略，覺得這個策略可能失效了，
變得說常常在優化策略，但是都是無謂的優化
Paper Trading 另一個關鍵是，你要把它當成真的$（雖然很難），
這樣操作的時候，除了模擬獲利，也模擬自己面對報酬率的心態，

接下來我們就進行三個步驟來做 Paper Trading 吧！

### 1. 安裝

這個程式沒什麼特別的安裝方法，可以打開anaconda prompt 輸入以下指令
```
git clone https://github.com/koreal6803/CmoneyVirtualAccount.git

# mac 使用的指令
mv CmoneyVirtualAccount/cmoneyVirtualAccount ./cmoney

# windows 使用的指令
move CmoneyVirtualAccount/cmoneyVirtualAccount ./cmoney
```

### 2. 申請帳號

我們要到 Cmoney 的平台來申請帳號密碼：
https://www.cmoney.tw/vt/
這邊值得注意的是，假如你有用FB登入，請還是要設定一個密碼，這樣等等才可以使用 Python 操控 Cmoney 的模擬平台喔！(右上角使用者名稱->基本資料)

### 3. 用程式操控
然後就可以在此資料夾中，使用 Python 來做 Paper trading 囉！
```
from cmoney.stock import VirtualStockAccmount, ProfitLossType

# 登入
vs = VirtualStockAccount('your_account', 'your_password')

# 切換子帳號
vs.aid = '123456'

# ------ #
# 查看帳戶
# ------ # 

# 拿到某檔股票的資料：
vs.get_price('2330')

# 查看目前帳戶持有的股票
vs.status()

# 查看現有資金
vs.info()


# 查看目前未實現損益
vs.profit_loss(profitLossType=ProfitLossType.UNACCOMPLISHED)

# 查看目前已實現損益
# startTime default = 180 days ago
# endTime default = today
vs.profit_loss(profitLossType=ProfitLossType.ACCOMPLISHED, startTime= "2020-01-01", endTime="2020-06-31")

# ------ #
# 操作帳戶
# ------ # 

# 買一張台積電（強迫現價或開盤價買入）
vs.buy('2330', 1)


# 賣出一張台積電（強迫現價或開盤賣出）
vs.sell('2330', 1)

# ------ #
# 批次操作
# ------ # 

# 買一張台積電、一張聯發科
vs.buy({'2330': 1, '2454': 1})

# 出清所有股票
vs.sell_all()

# 將所有帳戶持股設定成：「一張台積電」、「一張聯發科」
# （會先賣出股票，並且買「一張台積電」、「一張聯發科」)
vs.rebalance({'2330': 1, '2454': 1})

# 自動分配持股（平均分散總資產）（通常我會用這個）
vs.sync(['1101', '2330'])

# ------ #
# 委託操作
# ------ # 

# 查看目前的委託單
vs.get_orders()

# 刪除所有委託單
vs.cancel_all_orders()

```

### 課程同學 Bonus!


假如有上「小資族選股策略」的同學，想要paper trade你的策略，配合最後的優等生策略，可以直接使用：

```
vs.sync(strategy(data))
```

來 paper trade 任何選股策略喔！

這支程式放在倉庫裡很久了，最近想要用又把它拿出來，想說修理一下分享給大家！
也歡迎大家來 push 新功能喔～（缺 unit test 呀XD）
