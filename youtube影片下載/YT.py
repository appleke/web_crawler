import os
import re
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# 導入 yt-dlp
try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    print("警告: yt-dlp 套件未安裝，部分功能將不可用。請執行 'pip install yt-dlp' 安裝。")
    YTDLP_AVAILABLE = False
except Exception as e:
    print(f"警告: yt-dlp 導入時出錯: {e}，部分功能將不可用。")
    YTDLP_AVAILABLE = False

class YouTubeScraper:
    def __init__(self, output_dir="downloads"):
        """初始化 YouTube 爬蟲"""
        self.output_dir = output_dir
        # 確保下載目錄存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 檢查 yt-dlp 是否可用
        if not YTDLP_AVAILABLE:
            print("警告: 由於 yt-dlp 不可用，某些功能將受限。")
            
        # 檢查是否有 FFmpeg
        self.has_ffmpeg = self._check_ffmpeg()
        if not self.has_ffmpeg:
            print("警告: 未找到 FFmpeg，音訊轉換功能將受限。")
    
    def _check_ffmpeg(self) -> bool:
        """檢查系統是否安裝了 FFmpeg"""
        try:
            import subprocess
            result = subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0
        except Exception:
            return False
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """獲取 YouTube 影片的資訊"""
        try:
            # 從 URL 中提取影片 ID
            video_id = self._extract_video_id(url)
            if not video_id:
                print("錯誤: 無法從 URL 中提取影片 ID")
                return None
            
            # 使用 yt-dlp 獲取影片資訊
            if YTDLP_AVAILABLE:
                try:
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'skip_download': True,
                        'format': 'best',
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        # 確保 info 不是 None
                        if info is not None:
                            # 格式化資訊
                            video_info = {
                                "標題": info.get('title', '未知'),
                                "影片長度": self._format_duration(info.get('duration', 0)),
                                "觀看次數": info.get('view_count', 0),
                                "評分": info.get('average_rating', 0),
                                "發布日期": info.get('upload_date', '未知'),
                                "作者": info.get('uploader', '未知'),
                                "影片ID": video_id,
                                "縮圖網址": info.get('thumbnail', f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"),
                                "描述": info.get('description', '無描述')
                            }
                            return video_info
                        else:
                            print("yt-dlp 返回空資訊")
                except Exception as ydl_error:
                    print(f"yt-dlp 獲取影片資訊失敗: {ydl_error}")
            
            # 如果 yt-dlp 不可用或失敗，使用備用方法
            try:
                # 使用公開的 oEmbed API 獲取基本資訊
                oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                response = requests.get(oembed_url)
                if response.status_code == 200:
                    data = response.json()
                    info = {
                        "標題": data.get("title", "未知"),
                        "作者": data.get("author_name", "未知"),
                        "影片ID": video_id,
                        "縮圖網址": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    }
                    return info
            except Exception as alt_error:
                print(f"備用方法獲取影片資訊也失敗: {alt_error}")
                
            return None
        except Exception as e:
            print(f"獲取影片資訊時出錯: {e}")
            return None
    
    def download_video(self, url: str, resolution: str = "best", output_filename: Optional[str] = None) -> Optional[str]:
        """下載 YouTube 影片
        
        參數:
            url: YouTube 影片網址
            resolution: 解析度選項 ("best", "worst", "audio", "720p", "480p", "360p" 等)
            output_filename: 輸出檔案名稱 (不含副檔名)，如果為 None 則使用影片標題
            
        返回:
            下載的檔案路徑或 None (如果下載失敗)
        """
        if not YTDLP_AVAILABLE:
            print("錯誤: 此功能需要 yt-dlp 套件。")
            return None
            
        try:
            # 檢查是否有 FFmpeg，如果沒有且不是只下載音訊，提示用戶
            if not self.has_ffmpeg and resolution != "audio":
                print("警告: 未安裝 FFmpeg，無法合併影片和音訊。")
                print("建議安裝 FFmpeg: https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/")
                print("或選擇僅下載音訊選項。")
                
                # 詢問用戶是否繼續
                choice = input("是否繼續下載? (y/n): ")
                if choice.lower() != 'y':
                    print("下載已取消")
                    return None
                    
                print("將繼續下載，但影片和音訊將分開存儲。")
            
            # 準備下載選項
            ydl_opts = {
                'quiet': False,
                'no_warnings': True,
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'ignoreerrors': True,
            }
            
            # 如果有 FFmpeg，設置合併格式
            if self.has_ffmpeg:
                ydl_opts['merge_output_format'] = 'mp4'
            
            # 如果提供了輸出檔案名稱
            if output_filename:
                ydl_opts['outtmpl'] = os.path.join(self.output_dir, f"{output_filename}.%(ext)s")
            
            # 根據解析度設定格式
            if resolution == "best":
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            elif resolution == "worst":
                ydl_opts['format'] = 'worstvideo+worstaudio/worst'
            elif resolution == "audio":
                # 如果有 FFmpeg，使用音訊轉換
                if self.has_ffmpeg:
                    ydl_opts['format'] = 'bestaudio/best'
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                else:
                    # 如果沒有 FFmpeg，直接下載音訊，不轉換格式
                    print("注意: 由於未安裝 FFmpeg，將直接下載音訊格式，不會轉換為 MP3。")
                    ydl_opts['format'] = 'bestaudio/best'
            else:
                # 嘗試指定解析度，例如 "720p"
                height = resolution.rstrip("p")
                if height.isdigit():
                    ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best[height<={height}]'
                else:
                    ydl_opts['format'] = resolution
            
            # 獲取影片資訊以確定檔案名稱
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                # 確保 info 不是 None
                if info is None:
                    print("無法獲取影片資訊")
                    return None
                title = info.get('title', 'video')
                
            # 下載影片
            print(f"正在下載: {title}")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                
                # 檢查下載結果
                if result != 0:
                    print(f"下載過程中出現錯誤，返回碼: {result}")
            
            # 確定下載後的檔案路徑
            if output_filename:
                base_filename = output_filename
            else:
                # 處理檔案名稱中的非法字元和特殊字符
                base_filename = title
                
            # 處理檔案名稱中的非法字元和特殊字符
            base_filename = re.sub(r'[\\/*?:"<>|]', '_', base_filename)
            # 處理其他特殊字符，例如斜線變體
            base_filename = base_filename.replace('⧸', '_')
            base_filename = base_filename.replace('／', '_')
            base_filename = base_filename.replace('∕', '_')
            
            # 如果沒有 FFmpeg 且不是僅下載音訊，則需要找出下載的檔案
            if not self.has_ffmpeg and resolution != "audio":
                # 查找下載的檔案
                video_file = None
                audio_file = None
                
                for file in os.listdir(self.output_dir):
                    if base_filename in file:
                        if file.endswith('.mp4'):
                            video_file = os.path.join(self.output_dir, file)
                        elif file.endswith('.webm') or file.endswith('.m4a'):
                            audio_file = os.path.join(self.output_dir, file)
                
                if video_file and audio_file:
                    print(f"由於未安裝 FFmpeg，影片和音訊檔案分開存儲:")
                    print(f"影片檔案: {video_file}")
                    print(f"音訊檔案: {audio_file}")
                    return video_file  # 返回影片檔案路徑
                elif audio_file:
                    print(f"只找到音訊檔案: {audio_file}")
                    return audio_file
                elif video_file:
                    print(f"只找到影片檔案: {video_file}")
                    return video_file
            
            # 確定副檔名
            if resolution == "audio" and self.has_ffmpeg:
                file_ext = "mp3"
            else:
                file_ext = "mp4"  # 默認使用 mp4 作為合併後的格式
            
            # 完整檔案路徑
            file_path = os.path.join(self.output_dir, f"{base_filename}.{file_ext}")
            
            # 檢查檔案是否存在
            if os.path.exists(file_path):
                print(f"下載完成: {file_path}")
                return file_path
            else:
                # 嘗試查找任何可能的下載檔案
                found_files = []
                for file in os.listdir(self.output_dir):
                    # 使用更寬鬆的匹配條件
                    # 檢查標題的前幾個字符是否存在於檔案名中
                    if len(base_filename) > 5 and base_filename[:5] in file:
                        found_files.append(file)
                    # 或者檢查檔案名是否包含標題的一部分
                    elif len(base_filename) > 10 and any(part in file for part in base_filename.split()):
                        found_files.append(file)
                
                # 如果找到了檔案，使用最新的一個
                if found_files:
                    # 按修改時間排序，最新的在前面
                    found_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.output_dir, x)), reverse=True)
                    newest_file = os.path.join(self.output_dir, found_files[0])
                    print(f"下載完成: {newest_file}")
                    return newest_file
                        
                print("找不到下載的檔案")
                return None
                
        except Exception as e:
            print(f"下載影片時出錯: {e}")
            return None
    
    def search_videos(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜尋 YouTube 影片"""
        videos = []
        
        # 方法 1: 使用 yt-dlp (如果可用)
        if YTDLP_AVAILABLE:
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'extract_flat': True,
                    'default_search': 'ytsearch',
                    'ignoreerrors': True,
                }
                
                search_query = f"ytsearch{limit}:{query}"
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    search_results = ydl.extract_info(search_query, download=False)
                    
                    if search_results and 'entries' in search_results:
                        for entry in search_results['entries']:
                            if entry:
                                try:
                                    video_info = {
                                        "標題": entry.get('title', '未知'),
                                        "網址": entry.get('url', ''),
                                        "縮圖": entry.get('thumbnail', ''),
                                        "作者": entry.get('uploader', '未知'),
                                        "影片ID": entry.get('id', ''),
                                        "發布日期": entry.get('upload_date', '未知'),
                                        "影片長度": self._format_duration(entry.get('duration', 0))
                                    }
                                    videos.append(video_info)
                                except Exception as item_error:
                                    print(f"處理搜尋結果項目時出錯: {item_error}")
                                    continue
                
                if videos:
                    return videos
                else:
                    print("yt-dlp 搜尋未返回結果，嘗試替代方法")
            except Exception as e:
                print(f"yt-dlp 搜尋出錯: {e}，嘗試替代方法")
        
        # 方法 2: 使用替代方法 (簡單的 HTML 解析)
        try:
            # 使用簡單的請求模擬搜索
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
           
            response = requests.get(search_url)
            
            if response.status_code == 200:
                # 使用正則表達式提取影片 ID
                video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
                unique_ids = []
                
                # 去重
                for video_id in video_ids:
                    if video_id not in unique_ids:
                        unique_ids.append(video_id)
                        
                        if len(unique_ids) >= limit:
                            break
                
                # 獲取每個影片的基本資訊
                for video_id in unique_ids[:limit]:
                    try:
                        # 使用 oEmbed API 獲取基本資訊
                        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
                        vid_response = requests.get(oembed_url)
                        
                        if vid_response.status_code == 200:
                            data = vid_response.json()
                            video_info = {
                                "標題": data.get("title", "未知"),
                                "網址": f"https://www.youtube.com/watch?v={video_id}",
                                "縮圖": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                                "作者": data.get("author_name", "未知")
                            }
                            videos.append(video_info)
                    except Exception as item_error:
                        print(f"處理替代搜尋結果項目時出錯: {item_error}")
                        continue
        except Exception as alt_error:
            print(f"替代搜尋方法出錯: {alt_error}")
            
        return videos
    
    def _format_duration(self, seconds: int) -> str:
        """將秒數格式化為時:分:秒"""
        if not seconds:
            return "未知"
            
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            return f"{int(minutes):02d}:{int(seconds):02d}"
            
    def _extract_video_id(self, url: str) -> Optional[str]:
        """從 YouTube URL 中提取影片 ID"""
        # 處理常見的 YouTube URL 格式
        patterns = [
            r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",  # 標準和分享連結
            r"(?:embed\/)([0-9A-Za-z_-]{11})",  # 嵌入連結
            r"(?:shorts\/)([0-9A-Za-z_-]{11})"  # YouTube Shorts
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        return None


# 使用範例
if __name__ == "__main__":
    scraper = YouTubeScraper()
    
    # 檢查是否有 FFmpeg
    if not scraper.has_ffmpeg:
        print("警告: 未找到 FFmpeg，這會導致影片和音訊無法合併。")
        print("強烈建議安裝 FFmpeg 以獲得最佳下載體驗。")
        print("Windows 安裝指南: https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/")
        print("安裝後重啟程式。")
        print()
        print("若要繼續使用，請選擇「僅下載音訊」選項，或接受影片和音訊將分開存儲。")
        print()
    
    # 請使用者輸入 YouTube 影片連結
    video_url = input("請輸入 YouTube 影片連結: ")
    
    # 獲取影片資訊
    print("\n獲取影片資訊中...")
    info = scraper.get_video_info(video_url)
    if info:
        print("\n影片資訊:")
        for key, value in info.items():
            if key != "描述":  # 描述通常很長，所以不顯示
                print(f"{key}: {value}")
    
    # 詢問下載選項
    print("\n下載選項:")
    print("1. 最佳品質 (影片+音訊)")
    print("2. 僅下載音訊")
    print("3. 720p (影片+音訊)")
    print("4. 480p (影片+音訊)")
    print("5. 360p (影片+音訊)")
    
    choice = input("請選擇下載選項 (1-5): ")
    
    # 設定解析度
    resolution_options = {
        "1": "best",
        "2": "audio",
        "3": "720p",
        "4": "480p",
        "5": "360p"
    }
    
    resolution = resolution_options.get(choice, "best")
    
    # 下載影片
    print(f"\n正在以 {resolution} 品質下載影片...")
    downloaded_file = scraper.download_video(video_url, resolution=resolution)
    
    if downloaded_file:
        if scraper.has_ffmpeg or resolution == "audio":
            print(f"下載完成! 檔案已儲存至: {downloaded_file}")
        else:
            print("下載完成! 請注意查看上方顯示的檔案路徑。")
    else:
        print("下載失敗，請檢查連結是否正確或嘗試其他解析度。")
