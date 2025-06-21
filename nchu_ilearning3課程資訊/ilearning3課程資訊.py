import os
from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()
url = "https://lms2020.nchu.edu.tw/index/login?next=%2Fdashboard"
username =os.getenv("usernames")
password = os.getenv("password")

# 模擬登入
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)  # 設置瀏覽器分離
driver = webdriver.Chrome(options=chrome_options)
driver.get(url)#打開登入網頁


driver.find_element(By.XPATH, '//*[@id="account"]/div/input').send_keys(username)
driver.find_element(By.XPATH, '//*[@id="password"]/div/div[1]/input').send_keys(password)

#抓取驗證碼
captcah_input = driver.find_element(By.CSS_SELECTOR, "img.js-captcha")
captcah_input.screenshot("captcha.png")

import google.generativeai as genai
import base64

# 讀取圖片並轉為 base64
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")   
base64_img = encode_image('captcha.png')    

#輸入gemini api 和 系統指令
gemini_api = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=gemini_api)

system_instruction_text = "你是OCR辨識專家，請精確讀取圖片中的驗證碼，並只回傳驗證碼（不加註解、不加標點、沒有多餘文字）。"

# 使用 system_instruction 建立模型
client = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction_text
)

response = client.generate_content(
    contents=[
        {
            "role": "user",
            "parts": [
                {"text": "請讀取這張圖片的驗證碼，請只回傳驗證碼。"},
                {"inline_data": {"mime_type": "image/png", "data": base64_img}}
            ]
        }
    ],
)

driver.find_element(By.XPATH, '//*[@id="captcha"]/div/input').send_keys(response.text)
driver.find_element(By.XPATH, '//*[@id="login_form"]/div[7]/div/button').click()

from bs4 import BeautifulSoup
import time

time.sleep(3)
soup = BeautifulSoup(driver.page_source,'html.parser')

courses = soup.find_all('div',class_="fs-caption")

for a in courses:
    all_courses = a.find('div',class_='fs-label')
    print(all_courses.text)
    courses_hint = a.find('div',class_='fs-hint')
    print(courses_hint.text)