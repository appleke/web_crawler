from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

url = "https://shopping.pchome.com.tw/activity/collection.htm"

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # 設置瀏覽器分離
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)#打開登入網頁
html = driver.page_source
soup = BeautifulSoup(html,'html.parser')

#print(soup.prettify())

discount = soup.find_all('a',class_="slogan")

print("PChome 即時優惠活動：")
print("=" * 50)

# 使用集合來去除重複，因為PChome網頁上有多個相同的活動連結。
seen_activities = set()
unique_activities = []

for activity in discount:
    # 提取活動文字內容
    activity_text = activity.get_text(strip=True)
    
    # 提取連結
    activity_str = str(activity)
    if 'href=' in activity_str:
        start = activity_str.find('href="') + 6   # 網址從 href=" 的下一個開始所以+6
        end = activity_str.find('"', start)       #根據start找到下一個 " 的結束位置
        activity_link = activity_str[start:end] if start > 5 and end > start else '無連結'
    else:
        activity_link = '無連結'
    
    # 尋找日期資訊 - 在同一個父元素中尋找date class的span
    date_info = '無日期資訊'
    parent = activity.parent
    if parent:
        date_span = parent.find('span', class_='date')
        if date_span:
            date_info = date_span.get_text(strip=True)
    
    # 組合文字、日期和連結作為唯一識別
    activity_key = f"{activity_text}|{date_info}|{activity_link}"
    
    # 如果這個活動還沒出現過，就加入列表
    if activity_key not in seen_activities:
        seen_activities.add(activity_key)
        unique_activities.append((activity_text, date_info, activity_link))

# 輸出去重後的活動
for i, (activity_text, date_info, activity_link) in enumerate(unique_activities, 1):
    print(f"{i}. {activity_text}")
    print(f"   日期: {date_info}")
    print(f"   連結: {activity_link}")
    print("-" * 50)
driver.quit()



