# ble_plotter
received ble signal from xiao(esp32c3) and create realtime plot.  For human powered aircraft use.

【使い方】
・python ble.py で受信とCSV記録開始。plotter.pyが自動実行される。adafruit_bleのインストールが必要。
・フリーズしたりデータが途切れたりCSVファイルを新たにしたい場合は、python ble.pyをまた実行すればよい。


【蛇足】
・python plotter.py でCSV読み込みとグラフ表示を開始する。matplotlibのインストールが必要。
（要改善：毎ループ csv open して全データ読み込みしてしまっている。今の所、処理速度に影響ないので放置中。）
・serial_send_data.py や、sim_writecsv.py は開発用途なので普段は使用しない。
・録画は OBS Studio を推奨。Macではバックアップ手段として Command+Shift+5 で画面録画ができる。