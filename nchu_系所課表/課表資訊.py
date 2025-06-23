import time
import os
import json
from DrissionPage import ChromiumPage
from dotenv import load_dotenv

# 初始化 ChromiumPage
page = ChromiumPage()

# 訪問登入頁面
login_url = "https://ccidp.nchu.edu.tw/login?service=https://cportal.nchu.edu.tw/cas_login/&locale=zh-TW"
course_url = "https://cportal.nchu.edu.tw/cofsys/plsql/crseqry_home"

# 創建一個目錄來保存所有系所的課程資訊
if not os.path.exists("課程資訊"):
    os.makedirs("課程資訊")

# 系所代碼和名稱列表（直接從選單中複製）
departments = [
    {"code": "C10", "name": "文學院"},
    {"code": "C20", "name": "管理學院"},
    {"code": "C30", "name": "農業暨自然資源學院"},
    {"code": "C60", "name": "工學院"},
    {"code": "C70", "name": "法政學院"},
    {"code": "U10F", "name": "台灣人文創新學士學位學程"},
    {"code": "U11", "name": "中國文學系學士班"},
    {"code": "U12", "name": "外國語文學系學士班"},
    {"code": "U13", "name": "歷史學系學士班"},
    {"code": "U21", "name": "財務金融學系學士班"},
    {"code": "U23", "name": "企業管理學系學士班"},
    {"code": "U24", "name": "法律學系學士班"},
    {"code": "U28", "name": "會計學系學士班"},
    {"code": "U29", "name": "資訊管理學系學士班"},
    {"code": "U30F", "name": "景觀與遊憩學士學位學程"},
    {"code": "U30G", "name": "生物科技學士學位學程"},
    {"code": "U30H", "name": "國際農企業學士學位學程"},
    {"code": "U31", "name": "農藝學系學士班"},
    {"code": "U32", "name": "園藝學系學士班"},
    {"code": "U33A", "name": "森林學系林學組學士班"},
    {"code": "U33B", "name": "森林學系木材科學組學士班"},
    {"code": "U34", "name": "應用經濟學系學士班"},
    {"code": "U35", "name": "植物病理學系學士班"},
    {"code": "U36", "name": "昆蟲學系學士班"},
    {"code": "U37", "name": "動物科學系學士班"},
    {"code": "U38A", "name": "獸醫學系學士班"},
    {"code": "U38B", "name": "獸醫學系學士班"},
    {"code": "U39", "name": "土壤環境科學系學士班"},
    {"code": "U40", "name": "生物產業機電工程學系學士班"},
    {"code": "U42", "name": "水土保持學系學士班"},
    {"code": "U43", "name": "食品暨應用生物科技學系學士班"},
    {"code": "U44", "name": "行銷學系學士班"},
    {"code": "U51", "name": "化學系學士班"},
    {"code": "U52", "name": "生命科學系學士班"},
    {"code": "U53F", "name": "應用數學系應用數學組學士班"},
    {"code": "U53G", "name": "應用數學系數據科學與計算組學士班"},
    {"code": "U54A", "name": "物理學系一般物理組學士班"},
    {"code": "U54B", "name": "物理學系光電物理組學士班"},
    {"code": "U56", "name": "資訊工程學系學士班"},
    {"code": "U60G", "name": "智慧創意工程學士學位學程"},
    {"code": "U61B", "name": "機械工程學系學士班"},
    {"code": "U61A", "name": "機械工程學系學士班"},
    {"code": "U62A", "name": "土木工程學系學士班"},
    {"code": "U62B", "name": "土木工程學系學士班"},
    {"code": "U63", "name": "環境工程學系學士班"},
    {"code": "U64B", "name": "電機工程學系學士班"},
    {"code": "U64A", "name": "電機工程學系學士班"},
    {"code": "U64F", "name": "電機資訊學院學士班"},
    {"code": "U65", "name": "化學工程學系學士班"},
    {"code": "U66", "name": "材料科學與工程學系學士班"},
    {"code": "U86", "name": "學士後醫學系學士班"}
]

# 爬取指定系所的課程資訊
def scrape_department_courses(dept_code, dept_name):
    try:
        # 構建查詢URL
        query_url = f"{course_url}_now?v_dept={dept_code}"
        page.get(query_url)
        time.sleep(5)
        
        print(f"正在爬取 {dept_code} {dept_name} 的課程資訊...")
        
        # 提取課程表格數據
        courses = []
        
        # 使用JavaScript獲取表格數據
        js_code = """
        function extractTableData() {
            var tables = document.querySelectorAll('table[name="mytable"]');
            if (!tables || tables.length === 0) return { tables: [] };
            
            var result = { tables: [] };
            
            // 遍歷每個表格
            for (var t = 0; t < tables.length; t++) {
                var table = tables[t];
                var rows = table.querySelectorAll('tr');
                var tableData = { header: '', courses: [] };
                var hasCourses = false;
                
                // 獲取表格標題信息（第一行）
                if (rows.length > 0) {
                    var headerRow = rows[0];
                    var headerCell = headerRow.querySelector('td');
                    if (headerCell) {
                        var headerText = headerCell.innerText.trim();
                        var headerDiv = headerCell.querySelector('div.tablesorter-header-inner');
                        if (headerDiv) {
                            var strongElem = headerDiv.querySelector('strong');
                            if (strongElem) {
                                headerText = strongElem.innerText.trim();
                            }
                        }
                        tableData.header = headerText;
                    }
                }
                
                // 從第3行開始（跳過表頭）
                for (var i = 2; i < rows.length; i++) {
                    var row = rows[i];
                    var cells = row.querySelectorAll('td');
                    
                    if (cells.length >= 19) {
                        var course = {
                            '必選別': cells[0].innerText.trim(),
                            '選課號碼': cells[1].innerText.trim(),
                            '科目名稱': cells[2].innerText.trim(),
                            '先修科目': cells[3].innerText.trim(),
                            '全半年': cells[4].innerText.trim(),
                            '學分數': cells[5].innerText.trim(),
                            '上課時數': cells[6].innerText.trim(),
                            '實習時數': cells[7].innerText.trim(),
                            '上課時間': cells[8].innerText.trim(),
                            '實習時間': cells[9].innerText.trim(),
                            '上課教室': cells[10].innerText.trim(),
                            '實習教室': cells[11].innerText.trim(),
                            '上課教師': cells[12].innerText.trim(),
                            '實習教師': cells[13].innerText.trim(),
                            '開課單位': cells[14].innerText.trim(),
                            '開課人數': cells[15].innerText.trim(),
                            '外系人數': cells[16].innerText.trim(),
                            '可加選餘額': cells[17].innerText.trim(),
                            '授課語言': cells[18].innerText.trim()
                        };
                        
                        if (cells.length >= 20) {
                            course['備註'] = cells[19].innerText.trim();
                        }
                        
                        tableData.courses.push(course);
                        hasCourses = true;
                    }
                }
                
                // 只添加有課程的表格
                if (hasCourses) {
                    result.tables.push(tableData);
                }
            }
            
            return result;
        }
        
        return JSON.stringify(extractTableData());
        """
        
        # 執行JavaScript獲取表格數據
        table_data_json = page.run_js(js_code)
        
        if table_data_json and table_data_json != "{\"tables\":[]}":
            data = json.loads(table_data_json)
            tables = data.get('tables', [])
            
            # 合併所有表格的課程
            courses = []
            total_courses = 0
            
            for i, table_data in enumerate(tables):
                header = table_data.get('header', '')
                table_courses = table_data.get('courses', [])
                
                # 為每個課程添加標題信息並放在第一個位置
                for course in table_courses:
                    # 創建新的字典，將標題放在第一位
                    new_course = {'標題': header}
                    # 將原有的課程信息添加到新字典中
                    for key, value in course.items():
                        new_course[key] = value
                    # 替換原有的課程字典
                    table_courses[table_courses.index(course)] = new_course
                
                courses.extend(table_courses)
                total_courses += len(table_courses)
                
                print(f"表格 {i+1}: {header} - {len(table_courses)} 門課程")
            
            print(f"已爬取 {dept_code} {dept_name} 的課程資訊，共 {total_courses} 門課程")
        else:
            print(f"找不到課程表格或表格為空，系所: {dept_code}")
            courses = []
    except Exception as e:
        print(f"提取 {dept_code} 課程表格時出錯: {e}")
        courses = []
    
    # 保存課程數據為JSON
    with open(f"課程資訊/{dept_code}_{dept_name}.json", "w", encoding="utf-8") as f:
        json.dump(courses, f, ensure_ascii=False, indent=2)
    
    return courses

# 主函數
def main():
    try:
        # 登入系統
        page.get(login_url)
        time.sleep(3)
        
        # 填寫帳號
        load_dotenv()
        username = os.getenv("usernames")
        password = os.getenv("password")
        
        # 輸入帳號密碼
        time.sleep(2)
        page.ele('xpath://*[@id="username"]').input(username)
        page.ele('xpath://*[@id="password"]').input(password)
        
        # 點擊登入按鈕
        time.sleep(3) # 等待CF-turnstile機制加載完成
        
        login_button = page.ele('xpath://*[@id="login-form-controls"]/span/span/button/span').click()
        
        # 等待登入完成
        time.sleep(5)
        print("當前頁面標題:", page.title)
        
        # 保存系所列表
        with open("課程資訊/departments.json", "w", encoding="utf-8") as f:
            json.dump(departments, f, ensure_ascii=False, indent=2)
        
        print(f"總共有 {len(departments)} 個系所")
        
        # 爬取每個系所的課程
        all_courses = {}
        for dept in departments:
            dept_code = dept['code']
            dept_name = dept['name']
            
            courses = scrape_department_courses(dept_code, dept_name)
            all_courses[dept_code] = courses
            
            # 每爬取一個系所後暫停一下，避免請求過於頻繁
            time.sleep(2)
        
        # 保存所有課程數據
        with open("課程資訊/all_courses.json", "w", encoding="utf-8") as f:
            json.dump(all_courses, f, ensure_ascii=False, indent=2)
        
        print("所有系所課程資訊爬取完成！")
    except Exception as e:
        print(f"執行過程中出錯: {e}")

if __name__ == "__main__":
    try:
        main()
    finally:
        # 完成後等待用戶按下 Enter 鍵再關閉瀏覽器
        input("按 Enter 鍵關閉瀏覽器...")
        page.quit()


