# 🧒 Giải Thích Dự Án TechStore - Dễ Như Ăn Kẹo!

---

## 🏪 Câu chuyện bắt đầu: TechStore Vietnam là gì?

Tưởng tượng bạn mở một **cửa hàng bán điện thoại, laptop** ở Việt Nam. Cửa hàng này bán hàng ở **nhiều nơi khác nhau**:

| Kênh bán | Giống như... |
|----------|-------------|
| **Shopify** | Bán trên website (như Shopee) |
| **Sapo POS** | Bán tại quầy (khách đến cửa hàng mua trực tiếp) |
| **Online Orders** | Đơn hàng online khác |

Và khách hàng trả tiền bằng **nhiều cách**:

| Phương thức | Giống như... |
|-------------|-------------|
| **PayPal** | Chuyển tiền quốc tế |
| **MoMo** | Ví MoMo (quét QR) |
| **ZaloPay** | Ví ZaloPay (quét QR) |
| **Mercury** | Tài khoản ngân hàng của cửa hàng |

---

## 😵 Vấn đề: Dữ liệu nằm lung tung!

Hãy tưởng tượng:
- Dữ liệu bán hàng Shopify nằm ở **một chỗ**
- Dữ liệu bán hàng tại quầy nằm ở **chỗ khác**
- Dữ liệu thanh toán MoMo nằm ở **chỗ khác nữa**
- ...

> Giống như bạn có **7 cuốn sổ ghi chép khác nhau**, mỗi cuốn ghi theo kiểu riêng, chữ viết khác nhau, format khác nhau. Bạn muốn biết "tháng này lời bao nhiêu?" → Phải lật hết 7 cuốn sổ, tính tay → **RẤT MỆT!** 😩

---

## 💡 Giải pháp: Xây một "nhà máy xử lý dữ liệu" (ETL Pipeline)

Dự án này giống như xây một **nhà máy tự động**, có 3 bước:

```
 📦 E (Extract)     →    🔧 T (Transform)     →    📊 L (Load)
 LẤY dữ liệu ra         SỬA & SẮP XẾP lại        ĐƯNG VÀO kho
```

### Hãy tưởng tượng nó giống việc NẤU ĂN:

````carousel
### 📦 Bước 1: EXTRACT (Lấy nguyên liệu)

Giống như đi chợ mua đồ về:
- Đi **sạp thịt** (Shopify) → mua thịt 
- Đi **sạp rau** (Sapo) → mua rau
- Đi **sạp gia vị** (MoMo, PayPal...) → mua gia vị

> **Trong code:** Lấy dữ liệu từ **GCS** (Google Cloud Storage) 
> - GCS giống như một **cái tủ lạnh trên mây** ☁️ của Google
> - Dữ liệu được nén (.json.gz) giống như đồ đóng hộp chân không
> - Các file `extractors/` chính là "người đi chợ"

```
extractors/
├── base_extractor.py      ← "Kỹ năng đi chợ cơ bản" (biết mở tủ GCS)
├── shopify_extractor.py   ← "Đi sạp Shopify"
├── sapo_extractor.py      ← "Đi sạp Sapo"
├── payment_extractor.py   ← "Đi sạp thanh toán"
└── tracking_extractor.py  ← "Đi sạp theo dõi khách"
```
<!-- slide -->
### 🔧 Bước 2: TRANSFORM (Sơ chế & nấu)

Giống như rửa rau, cắt thịt, nêm gia vị:
- **Kiểm tra chất lượng**: Rau có bị hư không? (dữ liệu bị null, trùng lặp?)
- **Cắt gọn**: Bỏ phần không cần thiết
- **Sắp xếp**: Bày lên đĩa cho đẹp (đưa vào **Star Schema**)

> **Star Schema là gì?** 🌟
>
> Giống như sắp xếp đồ trong tủ quần áo:
> - **Ngăn kéo 1 (dim_customers)**: Thông tin khách hàng
> - **Ngăn kéo 2 (dim_products)**: Thông tin sản phẩm
> - **Ngăn kéo 3 (dim_locations)**: Thông tin cửa hàng
> - **Ngăn kéo 4 (dim_staff)**: Thông tin nhân viên
> - **Ngăn kéo 5 (dim_date)**: Lịch ngày tháng
>
> Và **5 bảng ghi chép chính (fact tables)**:
> - Sổ đơn hàng, sổ chi tiết đơn, sổ thanh toán, sổ hành vi khách, sổ ngân hàng

```
transformers/
├── base_transformer.py        ← "Kỹ năng nấu cơ bản" (kiểm tra, rửa, cắt)
├── dimension_transformer.py   ← "Sắp xếp ngăn kéo" (bảng dimension)
└── fact_transformer.py        ← "Ghi sổ" (bảng fact)
```
<!-- slide -->
### 📊 Bước 3: LOAD (Dọn ra bàn ăn)

Giống như bày đồ ăn lên bàn để mọi người ăn:
- Đưa dữ liệu đã sạch sẽ vào **BigQuery** (kho dữ liệu trên mây của Google)
- Tạo các **Views** (góc nhìn) để dễ phân tích

> **BigQuery giống như gì?** 
> - Giống một **bảng Excel siêu to**, nằm trên internet
> - Có thể chứa hàng **triệu dòng** mà vẫn chạy nhanh
> - Ai có quyền đều vào xem được

```
loaders/
└── bigquery_loader.py  ← "Người bày bàn" (đưa dữ liệu vào BigQuery)
```
````

---

## 🎯 Cuối cùng: Power BI Dashboard (Kết quả)

Sau khi dữ liệu đã nằm gọn gàng trong BigQuery, ta dùng **Power BI** để tạo **3 bảng báo cáo trực quan** (dashboard):

| Dashboard | Trả lời câu hỏi... |
|-----------|-------------------|
| 🛒 **Customer Journey** | Khách hàng biết đến mình từ đâu? Mua gì? Quay lại không? |
| 💰 **Cashflow** | Tiền vào ra bao nhiêu? Tháng nào lời? Tháng nào lỗ? |
| 💳 **Payment Status** | Đơn nào đã thanh toán? Đơn nào chờ? Đơn nào bị hủy? |

> Giống như bạn có **3 tấm bảng to treo trên tường** với biểu đồ đẹp, chỉ cần nhìn là hiểu ngay tình hình kinh doanh! 📊

---

## 🗺️ Tổng hợp: Bức tranh toàn cảnh

```
☁️ GCS (Tủ lạnh trên mây)
    │
    │  📦 EXTRACT (đi chợ lấy đồ)
    │  → shopify_extractor, sapo_extractor, payment_extractor...
    ▼
🔧 TRANSFORM (sơ chế, nấu nướng)
    │  → Kiểm tra chất lượng
    │  → Sắp xếp theo Star Schema (5 ngăn kéo + 5 cuốn sổ)
    ▼
📊 BigQuery (Bàn ăn siêu to trên mây)
    │  → Dữ liệu sạch, gọn gàng
    │  → 3 Views (góc nhìn phân tích)
    ▼
📱 Power BI (3 tấm bảng báo cáo đẹp)
    → Customer Journey
    → Cashflow
    → Payment Status
```

---

## 🤔 Giải thích thêm các từ khó

| Từ kỹ thuật | Giống như... |
|-------------|-------------|
| **ETL** | Extract-Transform-Load = Lấy → Sửa → Cất |
| **GCS** | Google Cloud Storage = Tủ lạnh trên mây |
| **BigQuery** | Bảng Excel siêu to trên mây |
| **Star Schema** | Cách sắp xếp tủ quần áo (ngăn kéo + sổ ghi chép) |
| **Pipeline** | Dây chuyền nhà máy tự động |
| **Power BI** | Phần mềm vẽ biểu đồ đẹp |
| **JSON** | Kiểu ghi dữ liệu (như viết nhật ký theo format) |
| **.gz** | File nén (như đóng hộp chân không cho nhỏ gọn) |
| **Dimension table** | Bảng mô tả (AI là ai? Cái gì? Ở đâu?) |
| **Fact table** | Bảng ghi sự kiện (Đã xảy ra chuyện gì? Bao nhiêu tiền?) |
| **View** | Một "cửa sổ nhìn" vào dữ liệu, gom nhiều bảng lại |
| **Orchestrator** | "Người quản lý nhà máy" - điều khiển hết 3 bước E, T, L |

---

## 📁 Hiểu cấu trúc thư mục

```
Final Project K41/
│
├── 📦 extractors/          ← Đội đi chợ (lấy dữ liệu)
├── 🔧 transformers/        ← Đội đầu bếp (sửa & sắp xếp dữ liệu)  
├── 📊 loaders/             ← Đội bày bàn (đưa vào BigQuery)
├── 🎯 orchestration/       ← Quản lý nhà máy (điều phối tất cả)
├── ⚙️ config/              ← Sổ hướng dẫn (cấu hình, mật khẩu)
├── 🧪 tests/               ← Đội kiểm tra chất lượng
├── 📝 utils/               ← Đồ dùng chung (viết nhật ký/log)
├── 📋 main.py              ← Nút BẬT nhà máy (chạy chương trình)
└── 📄 requirements.txt     ← Danh sách đồ cần mua (thư viện Python)
```

---

## ▶️ Cách chạy (đơn giản)

```bash
# Chạy toàn bộ nhà máy từ A-Z:
python main.py --full

# Chỉ đi chợ (lấy dữ liệu) thôi:
python main.py --extract

# Đi chợ + nấu nướng (không bày bàn):
python main.py --transform

# Xem thông tin bàn ăn (BigQuery):
python main.py --info
```

---

> [!TIP]
> **Tóm lại 1 câu:** Dự án này giống như xây một **nhà máy tự động** để gom hết dữ liệu bán hàng từ 7 nguồn khác nhau → dọn dẹp sạch sẽ → xếp gọn gàng vào 1 chỗ → rồi vẽ thành 3 bảng báo cáo đẹp để ông chủ nhìn vào hiểu ngay tình hình kinh doanh! 🚀
