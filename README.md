# sound-oekaki

sound-oekaki は 音で絵を書く、新しいスタイルのペインティングソフトです。

## Features
- 音によるペンスタイルの決定
	* 太さ
	* 濃さ
	* 色
	* ペン先スタイル

- 複数人による描画
	* WebSocketによる同期

- スマートフォン、タブレットへの対応 (**一部制限あり**)


## Authors
匙は投げられた＋α @ Hack U 2018 Nagoya

## Let's Try


## How to Use

### 1. Setup Server

1. Python 3.x のインストール

1. 必要パッケージのインストール

	- `ffmpeg`: 音声の変換  
		+ 各OS似合わせてコマンドラインツールをインストール  

		+ Python 用のラッパー `ffmpeg-python` をインストール    

		```bash  
		> pip3 install ffmpeg-python  
		```  

	- `REAPER`: Google製 音声解析フレームワーク  

	[GitHub - google/REAPER](https://github.com/google/REAPER)  

	- `tornado`: Python Web フレームワーク  
	
	```bash  
	> pip3 install torando  
	```  

	- `librosa`: 音声信号処理ライブラリ  
	
	```bash  
	> pip3 install librosa  
	```  

	- `numpy`: 行列計算ライブラリ  
	
	```bash  
	> pip3 install numpy  
	```  

	- `scipy`: 科学計算ライブラリ  
	
	```bash  
	> pip3 install scipy  
	```  

	- `opencv-python`: 画像処理ライブラリ  
	
	```bash  
	> pip3 install opencv-python  
	```  

	- `bezier`: ベジエ曲線用ライブラリ  
	
	```bash  
	> pip3 install bezier  
	```  


1. サーバーの起動  

```bash  
> python3 server.py  
```  

