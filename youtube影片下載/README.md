# YouTube 影片下載工具

這是一個基於 yt-dlp 的 YouTube 影片下載和資訊獲取工具，提供了簡單易用的 Python 介面。

## 功能特點

- 獲取 YouTube 影片的詳細資訊（標題、作者、觀看次數等）
- 下載 YouTube 影片（支援多種解析度選擇）
- 僅下載影片的音訊（如果有 FFmpeg 則轉換為 MP3 格式）
- 搜尋 YouTube 影片
- 自動檢測 FFmpeg 並適應不同環境

## 安裝需求

使用前需要安裝以下套件：

```bash
pip install yt-dlp requests
```

### FFmpeg 安裝 (強烈建議安裝)

**FFmpeg 是必要的**，如果要正確合併影片和音訊，或將音訊轉換為 MP3 格式。YouTube 通常將高品質的影片和音訊分開存儲，需要使用 FFmpeg 來合併它們：

- **Windows**: 
  1. 下載 FFmpeg: https://ffmpeg.org/download.html
  2. 解壓縮到一個目錄，例如 `C:\ffmpeg`
  3. 將 FFmpeg 的 bin 目錄添加到系統環境變數 PATH 中，例如 `C:\ffmpeg\bin`
  4. 重啟電腦或命令提示字元

- **macOS**: 
  ```bash
  brew install ffmpeg
  ```

- **Linux**: 
  ```bash
  sudo apt install ffmpeg  # Ubuntu/Debian
  sudo yum install ffmpeg  # CentOS/RHEL
  ```

如果未安裝 FFmpeg：
- 影片和音訊將會分開下載，無法合併成單一檔案
- 音訊將保留原始格式（通常是 webm 或 m4a），而不會轉換為 MP3
- 程式會顯示兩個檔案的路徑，讓你可以分別存取影片和音訊

### 直接執行腳本

直接執行 `YT.py` 腳本，它會提供互動式介面：

1. 輸入 YouTube 影片連結
2. 查看影片資訊
3. 選擇下載選項（最佳品質、僅音訊、720p、480p 或 360p）
4. 下載影片

<img src="爬蟲結果4.gif" alt="爬蟲結果4" width="640"/>  

## 錯誤處理

本工具包含多種錯誤處理機制：

1. 如果 yt-dlp 無法獲取影片資訊，會自動嘗試使用 YouTube oEmbed API 獲取基本資訊
2. 搜尋功能提供了備用方法，當 yt-dlp 搜尋失敗時會使用替代方法
3. 自動檢測 FFmpeg 是否可用，並相應調整下載方式
4. 若無 FFmpeg，會提示用戶並詢問是否繼續下載
5. 智能檔案名稱處理，避免因檔案名稱中的特殊字符導致問題

## 常見問題

**Q: 為什麼我下載的影片沒有聲音，或者影片和音訊是分開的檔案？**  
A: 這是因為未安裝 FFmpeg。YouTube 將高品質影片和音訊分開存儲，需要 FFmpeg 來合併它們。請按照上方的指南安裝 FFmpeg。

**Q: 如何確認 FFmpeg 已正確安裝？**  
A: 在命令提示字元或終端機中輸入 `ffmpeg -version`，如果顯示版本資訊，則表示安裝成功。

**Q: 下載失敗怎麼辦？**  
A: 可能是網路問題、YouTube 限制或 yt-dlp 版本過舊。嘗試更新 yt-dlp (`pip install -U yt-dlp`) 或選擇較低的解析度。

## 注意事項

- 請尊重 YouTube 的服務條款和版權法規。僅下載您有權下載的內容。
- 由於 YouTube 經常更新其 API 和網站結構，本工具可能需要定期更新以保持功能正常。
- 過度頻繁的請求可能會導致您的 IP 被 YouTube 暫時封鎖。
- 如果需要批量下載或更高級的功能，建議直接使用 yt-dlp 命令行工具。 