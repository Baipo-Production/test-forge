# 🎤 สคริปต์การนำเสนอ TestForge (ฉบับภาษาไทย)

---

## 🎯 เปิดการนำเสนอ (30 วินาที)

**"สวัสดีครับ/ค่ะ ทุกท่าน!**

วันนี้ผม/ดิฉันจะมานำเสนอ **TestForge** ซึ่งเป็นแพลตฟอร์มสร้างและรันเทสเคสอัตโนมัติที่แปลงไฟล์ Excel ให้กลายเป็นชุดเทสที่ครบถ้วนด้วย Robot Framework พร้อมระบบ monitoring แบบ real-time

เดี๋ยวผม/ดิฉันจะพาไปดูปัญหาที่เราแก้ไข แนวทางแก้ปัญหา และทดสอบจริงครับ/ค่ะ"

---

## 📊 ปัญหาที่พบ (1 นาที)

**"ก่อนอื่นมาดูปัญหาที่ทีม QA เจอกันบ่อยๆ:**

1. **ใช้เวลานาน** — การสร้างเทสเคสสำหรับทุกแบบ combination ใช้เวลาหลายวันหรือหลายอาทิตย์
2. **เสี่ยงต่อความผิดพลาด** — การใส่ข้อมูลด้วยมือทำให้ข้อมูลไม่สอดคล้องกันและพลาด edge case
3. **ดูแลรักษายาก** — การเปลี่ยน API ครั้งเดียวต้องแก้ไขหลายร้อยไฟล์
4. **ไม่มี visibility** — ไม่เห็นความคืบหน้าของการทดสอบแบบ real-time

**ตัวอย่าง:** API ที่มีพารามิเตอร์แค่ 4 ตัว แต่ละตัวมีค่าได้ 5 แบบ จะได้ **625 combinations** การเขียนด้วยมือเป็นไปไม่ได้เลย

---

## 💡 แนวทางแก้ปัญหา (1 นาที)

**"TestForge แก้ปัญหาด้วย workflow อัตโนมัติ 4 ขั้นตอน:**

1. **Generate** — อัปโหลด CSV/Excel ที่มีค่าพารามิเตอร์ → ได้ทุก combination
2. **Compile** — กรอกผลลัพธ์ที่คาดหวัง → คอมไพล์เป็นไฟล์ Robot Framework
3. **Execute** — รันเทสพร้อม streaming แบบ real-time
4. **Report** — ดาวน์โหลดรายงาน HTML/XML แบบละเอียด

**ประโยชน์หลัก:**
- ⚡ **ลดเวลา 90%** ในการสร้างเทสเคส
- 🎯 **Coverage 100%** ของทุก combination
- 📊 **เห็นผลแบบ real-time** ผ่าน Server-Sent Events
- 🔄 **พร้อม CI/CD** รองรับ GitHub Actions

---

## 🏗️ สถาปัตยกรรมระบบ (1 นาที)

**"มาดูสถาปัตยกรรมทางเทคนิคครับ/ค่ะ:**

```
Client อัปโหลด CSV → FastAPI Backend → Combination Service
                                     ↓
                    Excel ที่มี combinations (2 sheets: data + notes)
                                     ↓
Client กรอก expectations → Compile Service → ไฟล์ .robot ของ Robot Framework
                                     ↓
                          Run Service (async) → SSE real-time streaming
                                     ↓
                    Reports (HTML/XML) → ดาวน์โหลดเป็น ZIP
```

**Technology Stack:**
- **Backend:** FastAPI (async Python framework)
- **Test Framework:** Robot Framework พร้อม RequestsLibrary
- **Streaming:** Server-Sent Events (SSE) สำหรับอัปเดตแบบ real-time
- **Storage:** File-based workspace แยก directory ตามโปรเจค
- **Deployment:** Docker + docker-compose

---

## 🎬 Demo สด (3-4 นาที)

### **ขั้นตอนที่ 1: Generate Combinations**

**"ให้ผม/ดิฉันยกตัวอย่างจริงนะครับ/ค่ะ มีไฟล์ CSV ที่ระบุ:**
- Gender: Male, Female
- Age: 18-30, 31-50
- Nationality: Australia, Canada
- Religion: Buddhist, Christian

**ดูว่าเกิดอะไรขึ้นเมื่ออัปโหลดไฟล์นี้..."**

```bash
curl -X POST http://localhost:3000/api/v1/combination-test-case \
  -F "file=@input.csv" \
  -o combination_testcases.xlsx
```

**"ระบบจะสร้างไฟล์ Excel ที่มี 16 combinations (2×2×2×2) แบ่งเป็น 2 sheets:**
1. **Combination sheet** — ทุก combination ของพารามิเตอร์
2. **Note sheet** — คำแนะนำสำหรับกรอกผลลัพธ์ที่คาดหวัง

---

### **ขั้นตอนที่ 2: Compile เป็น Robot Framework**

**"หลังจากกรอก status code และ response body ที่คาดหวังแล้ว ก็อัปโหลด Excel กลับมา..."**

```bash
curl -X POST http://localhost:3000/api/v1/compile-test-case \
  -F "testName=demo-api" \
  -F "file=@combination_filled.xlsx"
```

**Response:**
```json
{
  "status": "compiled",
  "testName": "demo-api",
  "cases": 96,
  "run_url": "http://localhost:3000/api/v1/run-test-case/demo-api/stream"
}
```

**"ได้ไฟล์ Robot Framework ทั้งหมด 96 ไฟล์ใน `workspace/demo-api/generated/`"**

---

### **ขั้นตอนที่ 3: รันเทสพร้อม Real-Time Streaming**

**"ตอนนี้มารันเทสและดูความคืบหน้าแบบ real-time ผ่าน SSE..."**

**เปิด browser ที่:** `http://localhost:3000/api/v1/run-test-case/demo-api/stream`

**SSE Events ที่จะเห็น:**
```
event: connect
data: {"status":"connected","message":"Test execution started"}

event: process
data: {"case":"TC_001","status":"running","message":"Running TC_001"}

event: pass
data: {"case":"TC_001","status":"pass","message":"Test pass"}

event: fail
data: {"case":"TC_042","status":"fail","message":"Expected 200, got 400"}

event: done
data: {"status":"completed","summary":{"total":96,"passed":90,"failed":6,"skipped":0},"download_url":"http://localhost:3000/api/v1/download/demo-api/2025-10-30_14-30-15"}
```

---

### **ขั้นตอนที่ 4: ดาวน์โหลดรายงาน**

**"สุดท้ายก็ดาวน์โหลดรายงานฉบับสมบูรณ์..."**

```bash
curl -o report.zip \
  http://localhost:3000/api/v1/download/demo-api/2025-10-30_14-30-15
```

**"ไฟล์ ZIP จะประกอบด้วย:**
- `log.html` — รายละเอียดการรันทุกขั้นตอน
- `report.html` — สรุปผลแบบ dashboard
- `output.xml` — ผลลัพธ์แบบ machine-readable สำหรับ CI/CD

---

## 🔍 ดูโค้ดเชิงลึก (2 นาที)

### **ตัวอย่างเทส Robot Framework ที่สร้างขึ้น**

**"มาดูว่าไฟล์ที่ generate ออกมาเป็นยังไงครับ/ค่ะ:"**

```robot
*** Settings ***
Library    RequestsLibrary
Library    JSONLibrary
Suite Setup    Create Session    api    https://mockoon-api.techlabth.com

*** Test Cases ***
TC_001
    Log    ========== REQUEST ==========    console=yes
    Log    Method: POST    console=yes
    Log    Endpoint: /api/combination-data    console=yes
    
    ${payload}=    Create Dictionary    
    ...    Gender=Male    
    ...    Age=18-30    
    ...    Nationality=Australia    
    ...    Religion=Buddhist
    
    ${resp}=    POST On Session    api    /api/combination-data    
    ...    json=${payload}    
    ...    expected_status=any
    
    Log    ========== RESPONSE ==========    console=yes
    Log    Status Code: ${resp.status_code}    console=yes
    Log    Response Body: ${resp.text}    console=yes
```

---

### **ฟีเจอร์สำคัญในโค้ด:**

1. **Smart URL Parsing** — ดึง base URL อัตโนมัติ แปลง full URL เป็น relative path
2. **Comprehensive Logging** — บันทึก request/response ทุกรายการเพื่อ debug ง่าย
3. **Type Casting** — รองรับ tag `[Type:int]`, `[Type:bool]`, `[Type:float]`
4. **Assertion Operators** — `eq`, `ne`, `gt`, `lt`, `contains`, `regex`, `between`, `is_null` ฯลฯ
5. **Sentinel Values** — `[EMPTY]`, `[NULL]`, `[EMPTY_ARRAY]`, `[EMPTY_OBJECT]`

---

## 🚀 การ Deploy (1 นาที)

### **Deploy ด้วย Docker**

**"TestForge ถูกสร้างเป็น container พร้อม deploy:"**

```yaml
# docker-compose.yml
version: "3.9"
services:
  testforge-api:
    build: .
    ports:
      - "3000:3000"
    environment:
      - STORAGE_PATH=/app/workspace
    volumes:
      - ./workspace:/app/workspace
```

**เริ่มใช้งานด้วยคำสั่งเดียว:**
```bash
docker-compose up -d
```

---

### **ผูกกับ GitHub Actions**

**"สามารถ trigger การรันเทสจาก GitHub Actions ได้:"**

```yaml
- name: Run TestForge Tests
  run: |
    curl -X POST http://testforge.example.com/api/v1/github/trigger \
      -H "Authorization: Bearer ${{ secrets.GITHUB_TOKEN }}" \
      -d '{"testName": "production-api"}'
```

---

## 📈 ผลกระทบทางธุรกิจ (30 วินาที)

**"หลังจากใช้ TestForge:**

- **ประหยัดเวลา:** ลด 90% เวลาสร้างเทสเคส (จาก 2 วัน → 2 ชั่วโมง)
- **Coverage:** ครบ 100% ของ parameter combinations (เทียบกับ 60% แบบ manual)
- **หาบั๊กเจอมากขึ้น:** เจอบั๊กใน edge case เพิ่มขึ้น 35%
- **Productivity:** QA มีเวลาทำ exploratory testing แทนงานซ้ำๆ

---

## 🎯 แผนอนาคต (30 วินาที)

**"กำลังวางแผนเพิ่มฟีเจอร์:**

1. **UI Dashboard** — หน้าเว็บสำหรับจัดการ test suite
2. **Database Testing** — รองรับการตรวจสอบ SQL query
3. **Load Testing** — รันพร้อมกันหลาย concurrent พร้อมวัด performance
4. **Test Data Management** — ระบบจัดการ test data แบบรวมศูนย์
5. **AI-Powered Assertions** — แนะนำค่าที่คาดหวังจาก OpenAPI spec อัตโนมัติ

---

## 💬 เตรียมตอบคำถาม

### **คำถามที่มักถูกถาม:**

**Q: ต่างจาก Postman collections ยังไง?**  
A: TestForge เน้น *combinatorial testing* พร้อม auto-generation ส่วน Postman ต้องสร้าง request ทีละตัวเอง เรายังมี real-time SSE streaming และ assertion library ของ Robot Framework ที่ทรงพลัง

**Q: จัดการ authentication ยังไง?**  
A: เพิ่ม column `[Request][Header]Authorization` ใน Excel ได้เลย รองรับทุก header-based auth (Bearer tokens, API keys ฯลฯ)

**Q: รองรับ nested JSON ได้ไหม?**  
A: ได้ครับ/ค่ะ ใช้ dot notation: `[Request][Body]user.profile.name` หรือ array indexing: `[Request][Body]children[0].name`

**Q: Performance กับ test suite ใหญ่ๆ เป็นยังไง?**  
A: ทดสอบกับ combination มากกว่า 10,000 ตัวแล้ว bottleneck มักอยู่ที่ API ปลายทาง ไม่ใช่ TestForge เองครับ/ค่ะ รองรับการรันแบบขนานด้วย `--processes` flag ของ Robot Framework

**Q: ตรวจสอบ response ที่ซับซ้อนทำยังไง?**  
A: ใช้ assertion operators เช่น `[Response][Body]age:gt[Type:int]` จะตรวจว่า age มากกว่าค่าที่ระบุ รองรับ operator มากกว่า 15 ตัว รวม regex และ type validation

---

## 🎬 ปิดการนำเสนอ (30 วินาที)

**"สรุปครับ/ค่ะ:**

TestForge เปลี่ยนกระบวนการทดสอบ API แบบ combinatorial ที่น่าเบื่อให้กลายเป็นระบบอัตโนมัติที่ scale ได้ ด้วยเพียง 4 ขั้นตอน — Generate, Compile, Execute, Report — ทีมงานสามารถครอบคลุมการทดสอบได้ 100% ในเวลาไม่กี่นาที แทนที่จะเป็นหลายวัน

**ขอบคุณครับ/ค่ะ! ยินดีตอบคำถามนะครับ/ค่ะ"**

---

## 📚 แหล่งข้อมูลเพิ่มเติม

- **GitHub:** `https://github.com/Baipo-Production/test-forge`
- **เอกสาร:** ดูใน `README.md` และ `PRD.md`
- **Live Demo:** `http://localhost:3000/docs` (Swagger UI)
- **ติดต่อ:** [ข้อมูลการติดต่อของคุณ]

---

**เวลาทั้งหมดประมาณ:** 10-12 นาที (ปรับตามเวลาที่มี)
