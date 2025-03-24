# ble_plotter

人力飛行機（ダイダロス機）の試験飛行において、機体からBLEで送られたデータをリアルタイムにグラフ表示する。
受信したBLEデータはCSV保存も同時に行う。Macの標準のBluetoothで受信することができる。

![無線ロガー電装システム図](https://github.com/MasaoC/ble_plotter/assets/6983713/99f55044-6ccb-4f4f-a903-ae3f5c878cd6)


## 機能
- ble.py
    - BLE(Nordic UART)を受信する。BLE受信は、UART [NUS (Nordic UART Service) ] を通して行われる。
    - 2つ同時のBLE受信を試みる。片方のみでも動作する。これは機体からの直接信号およびリレーからの信号の２台同時受信を想定している。
    - plotter.pyが自動実行される。
    - 受信したデータは、ファイル記録を行う。現在のディレクトリにCSVフォルダを生成する。生データは下記ファイルに保存される。
      ```
      RAWDATAPATH = "./csv/raw.csv"
      RAWDATAPATH_RELAY = "./csv/raw_relay.csv"
      ```
    - 受信したBLEデータのうちカンマ区切りで正しく認識できたデータのみ、機体・リレーそれぞれ分けて日時のファイル名をつけてCSV保存される。保存時には現在時刻(msまで）がデータ先頭に追加され保存される。
    - 日付付きのCSVファイル名は、setting_plotter.txt に保存され、plotter.pyで利用される。
    - pip install adafruit-circuitpython-ble が必要。
    - pip install colorama が必要。
    - pip install matplotlib が必要。（plotter.pyが自動実行されるため）
- plotter.py
    - setting_plotter.txt を開き、ble.pyが保存している最新のCSVファイル２つを開く。
    - リアルタイムに更新されている上記CSVファイルのデータから、人力飛行機のラダー・エレベーター・速度計を表示する。
    - それぞれのCSVファイルの最終受信時刻を比較し、より新しい方のデータを随時グラフ表示する。どちらが利用されているかわかるように、グラフ上にDirect or Relayの表示がされる。
    - pip install matplotlib のインストールが必要
 
- createmovie.py
    - CSVから動画(mp4)を後から生成できる。リアルタイム録画できなかった場合でも、動画が作れる。
    - SDカードに保存された各種データを可視化するためのもの。
    - ffmpegのインストールが必要。

## 補足
- フリーズしたりデータが途切れたりCSVファイルを新たにしたい場合は、python ble.pyをまた実行すればよい。
- ble.py の下記定数を変えることで、BLEの名前を任意に変更できる。
  ```
  NAME_OLED = "ALBA TAIYO OLED v2"
  NAME_RELAY = "BLE RELAY"
  ```
- BLE送信機には、ESP32C3 XIAOを２つ使用した。 [送信機のArduinoプログラム](https://github.com/MasaoC/uart2ble_oled)
- serial_send_data.py や、sim_writecsv.py は開発用途なので普段は使用しない。
- 試験飛行における画面の録画は複数画面を録画できる OBS Studio を推奨。EOS Webcam Utilityと組み合わせることで、フライト映像と合成録画が可能。
- 要改善：毎ループ csv open して全データ読み込みしてしまっている。今の所、処理速度に影響ないので放置中。
