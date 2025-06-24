import os
import re
import time
import random
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

# 嘗試導入 pytube，如果失敗則提供錯誤信息
try:
    from pytube import YouTube, Search
    PYTUBE_AVAILABLE = True
except ImportError:
    print("警告: pytube 套件未安裝，部分功能將不可用。請執行 'pip install pytube' 安裝。")
    PYTUBE_AVAILABLE = False
except Exception as e:
    print(f"警告: pytube 導入時出錯: {e}，部分功能將不可用。")
    PYTUBE_AVAILABLE = False

class YouTubeScraper:
    def __init__(self, output_dir="downloads"):
        """初始化 YouTube 爬蟲"""
        self.output_dir = output_dir
        # 確保下載目錄存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 檢查 pytube 是否可用
        if not PYTUBE_AVAILABLE:
            print("警告: 由於 pytube 不可用，某些功能將受限。")
    
    def get_video_info(self, url: str) -> Optional[Dict[str, Any]]:
        """獲取 YouTube 影片的資訊"""
        if not PYTUBE_AVAILABLE:
            print("錯誤: 此功能需要 pytube 套件。")
            return None
            
        try:
            # 從 URL 中提取影片 ID
            video_id = self._extract_video_id(url)
            if not video_id:
                print("錯誤: 無法從 URL 中提取影片 ID")
                return None
                
            # 使用 pytube 嘗試獲取影片資訊
            try:
                yt = YouTube(url)
                info = {
                    "標題": yt.title,
                    "影片長度": self._format_duration(yt.length),
                    "觀看次數": yt.views,
                    "評分": yt.rating,
                    "發布日期": yt.publish_date.strftime("%Y-%m-%d") if yt.publish_date else "未知",
                    "作者": yt.author,
                    "影片ID": yt.video_id,
                    "縮圖網址": yt.thumbnail_url
                }
                return info
            except Exception as pytube_error:
                print(f"pytube 獲取影片資訊失敗: {pytube_error}")
                
                # 嘗試使用替代方法 (YouTube Data API)
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
                    print(f"替代方法獲取影片資訊也失敗: {alt_error}")
                    
                return None
        except Exception as e:
            print(f"獲取影片資訊時出錯: {e}")
            return None
    
    def download_video(self, url: str, resolution: str = "highest") -> Optional[str]:
        """下載 YouTube 影片"""
        if not PYTUBE_AVAILABLE:
            print("錯誤: 此功能需要 pytube 套件。")
            return None
            
        try:
            # 添加重試機制
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    yt = YouTube(url)
                    print(f"正在下載: {yt.title}")
                    
                    video = None
                    if resolution == "highest":
                        # 下載最高解析度的影片
                        video = yt.streams.get_highest_resolution()
                    elif resolution == "lowest":
                        # 下載最低解析度的影片
                        video = yt.streams.get_lowest_resolution()
                    elif resolution == "audio":
                        # 僅下載音訊
                        video = yt.streams.get_audio_only()
                    else:
                        # 嘗試下載指定解析度的影片，如果不可用則下載最高解析度
                        video = yt.streams.filter(res=resolution).first() or yt.streams.get_highest_resolution()
                    
                    # 確保獲取到了有效的影片流
                    if video is None:
                        print("無法獲取有效的影片流")
                        if attempt < max_retries - 1:
                            wait_time = (attempt + 1) * 2
                            print(f"等待 {wait_time} 秒後重試...")
                            time.sleep(wait_time)
                            continue
                        return None
                        
                    # 下載影片
                    file_path = video.download(output_path=self.output_dir)
                    
                    # 如果是僅音訊，將檔案重命名為 mp3
                    if resolution == "audio":
                        base, _ = os.path.splitext(file_path)
                        new_file_path = base + ".mp3"
                        os.rename(file_path, new_file_path)
                        file_path = new_file_path
                        
                    print(f"下載完成: {file_path}")
                    return file_path
                    
                except Exception as retry_error:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        print(f"下載時出錯: {retry_error}")
                        print(f"等待 {wait_time} 秒後重試...")
                        time.sleep(wait_time)
                    else:
                        print(f"達到最大重試次數，下載失敗: {retry_error}")
                        return None
                        
        except Exception as e:
            print(f"下載影片時出錯: {e}")
            return None
    
    def search_videos(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """搜尋 YouTube 影片"""
        videos = []
        
        # 方法 1: 使用 pytube (如果可用)
        if PYTUBE_AVAILABLE:
            try:
                search_results = Search(query)
                if search_results and search_results.results:
                    for i, result in enumerate(search_results.results):
                        if i >= limit:
                            break
                        
                        try:
                            video_info = {
                                "標題": result.title,
                                "網址": f"https://www.youtube.com/watch?v={result.video_id}",
                                "縮圖": result.thumbnail_url,
                                "作者": result.author,
                                "發布日期": result.publish_date.strftime("%Y-%m-%d") if result.publish_date else "未知",
                                "影片長度": self._format_duration(result.length) if hasattr(result, 'length') else "未知"
                            }
                            videos.append(video_info)
                        except Exception as item_error:
                            print(f"處理搜尋結果項目時出錯: {item_error}")
                            continue
                            
                if videos:
                    return videos
                else:
                    print("pytube 搜尋未返回結果，嘗試替代方法")
            except Exception as e:
                print(f"pytube 搜尋出錯: {e}，嘗試替代方法")
        
        # 方法 2: 使用替代方法 (簡單的 HTML 解析)
        try:
            # 使用簡單的請求模擬搜索
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(search_url, headers=headers)
            
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
                            
                            # 避免請求過於頻繁
                            time.sleep(0.5)
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
    
    # 範例 1: 獲取影片資訊
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 替換成你想要的影片網址
    print("\n嘗試獲取影片資訊...")
    info = scraper.get_video_info(video_url)
    if info:
        print("\n影片資訊:")
        for key, value in info.items():
            print(f"{key}: {value}")
    
    # 範例 2: 搜尋影片
    search_query = "Python 教學"
    print(f"\n搜尋 '{search_query}' 的結果:")
    results = scraper.search_videos(search_query, limit=3)
    
    if results:
        for i, video in enumerate(results, 1):
            print(f"\n結果 {i}:")
            for key, value in video.items():
                print(f"{key}: {value}")
    else:
        print("沒有找到相關影片")
    
    # 範例 3: 下載影片 (預設情況下註解掉以避免意外下載)
    # 取消下方註解以啟用下載功能
    # print("\n下載示範影片:")
    # downloaded_file = scraper.download_video(video_url, resolution="720p")
    # if downloaded_file:
    #     print(f"檔案已儲存至: {downloaded_file}")
    
    # 範例 4: 僅下載音訊
    # print("\n下載示範影片的音訊:")
    # audio_file = scraper.download_video(video_url, resolution="audio")
    # if audio_file:
    #     print(f"音訊檔案已儲存至: {audio_file}")
