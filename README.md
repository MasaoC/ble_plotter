# ble_plotter

人力飛行機（ダイダロス機）の試験飛行において、機体からBLEで送られたデータをリアルタイムにグラフ表示する。
受信したBLEデータはCSV保存も同時に行う。Macの標準のBluetoothで受信することができる。

![無線ロガー電装システム図](https://github.com/MasaoC/ble_plotter/assets/6983713/99f55044-6ccb-4f4f-a903-ae3f5c878cd6)


## Dependency/Install
    - pip install adafruit-circuitpython-ble
    - pip install colorama
    - pip install matplotlib
    - pip install --upgrade bleak

## 機能
- ble.py
    - BLE(Nordic UART)を受信する。BLE受信は、UART [NUS (Nordic UART Service) ] を通して行われる。
    - BLEの受信能力は端末に依存する。Macbook airで検証したところ、RELAYからの電波の受信可能距離は10m程度までは実験済み。
    - 2つ同時のBLE受信を試みる。片方のみでも動作する。これは機体からの直接信号およびリレーからの信号の２台同時受信を想定している。
    - plotter.pyが自動実行される。
    - 受信したデータは、ファイル記録を行う。現在のディレクトリにCSVフォルダを生成する。生データは下記ファイルに保存される。
      ```
      RAWDATAPATH = "./csv/raw.csv"
      RAWDATAPATH_RELAY = "./csv/raw_relay.csv"
      ```
    - 受信したBLEデータのうちカンマ区切りで正しく認識できたデータのみ、機体・リレーそれぞれ分けて日時のファイル名をつけてCSV保存される。保存時には現在時刻(msまで）がデータ先頭に追加され保存される。
    - 日付付きのCSVファイル名は、setting_plotter.txt に保存され、plotter.pyで利用される。
- usbcom_logger.py
    - BLEを介さず、USBから繋がっているCOMポートを開きCSVファイルに保存する。（RELAYのXIAOを直接USBポートを繋いだ想定だが、COMポートならなんでもOK）
    - 受信したデータは、ファイル記録を行う。現在のディレクトリにCSVフォルダを生成する。生データは下記ファイルに保存される。
      ```
      RAWDATAPATH = "./csv/raw.csv"
      ```
    - plotter.pyが自動実行されないので、可視化する時には手動で起動する。
    - COM経由で受信したデータのうちカンマ区切りで正しく認識できたデータのみ、日時のファイル名をつけてCSV保存される。保存時には現在時刻(msまで）がデータ先頭に追加され保存される。
- plotter.py
    - setting_plotter.txt を開き、ble.pyが保存している最新のCSVファイル２つを開く。
    - リアルタイムに更新されている上記CSVファイルのデータから、人力飛行機のラダー・エレベーター・速度計を表示する。
    - それぞれのCSVファイルの最終受信時刻を比較し、より新しい方のデータを随時グラフ表示する。どちらが利用されているかわかるように、グラフ上にDirect or Relayの表示がされる。
    - 動作例。<img width="390" alt="スクリーンショット 2025-06-03 21 35 41" src="https://github.com/user-attachments/assets/0104fc3f-64ad-4f10-8a7f-9b6a7bee3547" />

 
- createmovie.py
    - CSVから動画(mp4)を後から生成できる。スクリーンキャプチャーやOBSソフト等によってリアルタイムで録画できなかった場合でも、CSVからいつでも動画が作れる。
    - 用途としては、機体搭載のSDカードに保存された各種データを可視化するためのもの。CSVから動画生成には現状対応していない。
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
