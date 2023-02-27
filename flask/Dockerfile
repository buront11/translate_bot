# Pythonのversionは3.10を指定
FROM python:3.10
# バッファを溜めなくする処理。早くなるらしい。
ENV PYTHONUNBUFFERED 1 
# /codeディレクトリを作成
RUN mkdir /code
# 作業ディレクトリをWORKDIRに設定　おそらくプログラムを実行するディレクトリが/code内になると思われる
WORKDIR /code
# 同ディレクトリ内にあるrequirements.txtを/code/内に追加する
ADD requirements.txt /code/
# 必要なパッケージをインストール
RUN pip install -r requirements.txt
# その他諸々必要なものを追加
ADD . /code/