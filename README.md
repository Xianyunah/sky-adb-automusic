# sky-adb-automusic
The 'Sky' auto piano-playing script based on Python and ADB Shell.


## 软件使用.skym格式.
你只需要从sky music studio中将导出的.txt文件改名为xxx.skym即可使用

## 配置文件说明
首次运行时，软件会自动生成一个名为 `config.ini` 的配置文件，你需要根据设备配置调整以下参数：

### 配置项
- **adb_cmd**: ADB 命令，用于发送触摸事件，默认为 `input tap`。
- **use_wireless**: 是否启用无线调试功能，填 `true` 表示启用，填 `false` 表示关闭。
- **wireless_ip**: 无线设备的 IP 地址，当 `use_wireless` 设置为 `true` 时需指定。
- **wireless_port**: 无线设备的端口，通常为 `5555`。

### 坐标映射
[KeyMapping] 部分定义了每个按键对应的屏幕坐标。按键格式为 `1KeyX` 和 `2KeyX`（其中 X 为数字 0~14）。你可以根据设备屏幕分辨率调整这些坐标。

### 示例
```ini
[Settings]
adb_cmd = input tap
use_wireless = false
wireless_ip = 192.168.1.101
wireless_port = 5555

[KeyMapping]
1Key0 = 900,220
1Key1 = 1100,220
...
2Key14 = 1650,580
```

---




Here are the English and Japanese translations of your README:

---


### Using `.skym` Format  
To use the software, simply rename the `.txt` file exported from Sky Music Studio to `xxx.skym`.

### Configuration File Instructions  
On first launch, the software will automatically generate a file named `config.ini`. You need to adjust the following parameters based on your device configuration:

#### Configuration Items
- **adb_cmd**: ADB command for sending touch events. Default is `input tap`.  
- **use_wireless**: Whether to enable wireless debugging. Set to `true` to enable, or `false` to disable.  
- **wireless_ip**: The IP address of the wireless device. Required when `use_wireless` is set to `true`.  
- **wireless_port**: The port of the wireless device, usually `5555`.

#### Coordinate Mapping
The `[KeyMapping]` section defines the screen coordinates corresponding to each key. Key format is `1KeyX` and `2KeyX` (where X is a number from 0 to 14). Adjust these coordinates based on your device's screen resolution.

#### Example
```ini
[Settings]
adb_cmd = input tap
use_wireless = false
wireless_ip = 192.168.1.101
wireless_port = 5555

[KeyMapping]
1Key0 = 900,220
1Key1 = 1100,220
...
2Key14 = 1650,580
```

---


### `.skym`形式の使用方法  
Sky Music Studio からエクスポートされた `.txt` ファイルを `xxx.skym` にリネームするだけで使用できます。

### 設定ファイルの説明  
初回起動時に、ソフトウェアは自動的に `config.ini` という名前の設定ファイルを生成します。以下のパラメータは、デバイスに応じて調整してください。

#### 設定項目
- **adb_cmd**: タッチイベントを送信するための ADB コマンド。デフォルトは `input tap`。  
- **use_wireless**: ワイヤレスデバッグを有効にするかどうか。`true` で有効、`false` で無効。  
- **wireless_ip**: ワイヤレス接続するデバイスの IP アドレス。`use_wireless` が `true` の場合に指定が必要。  
- **wireless_port**: ワイヤレスデバイスのポート。通常は `5555`。

#### 座標マッピング
`[KeyMapping]` セクションでは、各キーに対応する画面上の座標を定義します。キーの形式は `1KeyX` または `2KeyX`（X は 0～14 の数字）。デバイスの画面解像度に応じて調整してください。

#### 例
```ini
[Settings]
adb_cmd = input tap
use_wireless = false
wireless_ip = 192.168.1.101
wireless_port = 5555

[KeyMapping]
1Key0 = 900,220
1Key1 = 1100,220
...
2Key14 = 1650,580
```

---




## License
This project is licensed under the **GNU AGPL-3.0 with additional restrictions**:
- ❌ **No commercial use** allowed
- 🔓 Modified versions must also be open source
- 🪧 Attribution is required  
See the [LICENSE](./LICENSE) file for details.

## Author
Created by Xianyunah 
If you wish to use this project commercially, please contact me for licensing.
