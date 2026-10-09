# 「初心」宣傳影片製作程式

| 檔案 | 用途 |
|---|---|
| `render.js` | 用無頭瀏覽器播放 `preview/chuxin-full.html`，每 1/30 秒截圖，合成無聲影片 |
| `music.py` | 程式合成配樂（合成配樂版使用） |

## 天祥真言配樂版

取自《天祥真言》冥想錄音的 1:30.4～2:22.4（共 52 秒）。
原曲在 2:01 加入低沉長音，剪輯後剛好落在影片第 31 秒「再次出發」。
處理：40 Hz 高通、增益 +7.6 dB、峰值限制 -1 dB、淡入 1.5 秒、淡出 2.4 秒，整體約 -16 LUFS。

```bash
ffmpeg -ss 90.4 -t 52 -i 天祥真言.m4a -af "highpass=f=40,volume=7.6dB,alimiter=limit=0.89:level=false,afade=t=in:d=1.5,afade=t=out:st=49.6:d=2.4,aresample=44100,pan=stereo|c0=c0|c1=c0" bgm.wav
ffmpeg -i video.mp4 -i bgm.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart 輸出.mp4
```
