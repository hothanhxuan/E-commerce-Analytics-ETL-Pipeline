# 🔬 So Sánh 2 Dự Án ETL Pipeline

> **Kết luận: Dự án của bạn tốt hơn rõ rệt** ở hầu hết mọi mặt kỹ thuật.
> Điểm: **Bạn 17 — hdangnguyen 2 — Hòa 1**

---

## 📊 Bảng Tổng Quan

| Tiêu chí | 🟢 Dự án của bạn | 🔵 hdangnguyen |
|---|---|---|
| **Số bảng dữ liệu** | **10 bảng** (5 dim + 5 fact) | 7 bảng (2 dim + 5 fact) |
| **Giao diện dòng lệnh** | ✅ 4 chế độ chạy | ❌ Chỉ 1 cách chạy |
| **Tiết kiệm bộ nhớ RAM** | ✅ Xử lý từng phần nhỏ | ❌ Nạp hết vào RAM |
| **View phân tích** | ✅ 3 views tự tạo | ❌ Không có |
| **File cấu hình** | ✅ YAML rõ ràng | ❌ Viết cứng trong code |
| **Bảng thời gian (dim_date)** | ✅ Tự tạo 2024–2027 | ❌ Không có |
| **Mã khóa (surrogate key)** | ✅ MD5 hash — an toàn | ⚠️ Nối chuỗi — dễ trùng |

---

## 1. 🏗️ Kiến Trúc — Cách Tổ Chức "Nhà Máy"

### Bạn — Nhà máy chạy theo **ca** (Phased)

Giống nhà máy chia ca sản xuất: **xong ca này → dọn dẹp → chạy ca tiếp**.

```
Ca A: Làm bảng Dimension → xong → dọn RAM
Ca B: Làm đơn hàng (orders) → xong → dọn RAM
Ca C: Làm thanh toán (payments) → xong → dọn RAM
Ca D: Làm sự kiện giỏ hàng (cart events) → xử lý TỪNG PHẦN NHỎ → dọn RAM
Ca E: Làm giao dịch ngân hàng → xong → dọn RAM
Ca F: Cập nhật tổng hợp + tạo Views
```

**Tại sao tốt?**
- File cart events nặng ~269MB. Nếu nạp hết vào RAM → máy 8GB sẽ **đứng máy**
- Bạn xử lý **50,000 dòng mỗi lần** (chunked) → không bao giờ quá tải
- Sau mỗi ca, gọi `gc.collect()` = **ra lệnh Python dọn rác** trong bộ nhớ

### hdangnguyen — Nhà máy chạy **liên tục** không dọn

Giống nấu ăn mà **không rửa nồi** giữa các món — cuối cùng bếp hết chỗ.

```
Bước 1: Làm tất cả Dimensions
Bước 2: Làm tất cả Facts (giữ hết dữ liệu trong RAM)
Bước 3: Cập nhật RFM (đang bị tắt/commented out!)
```

**Vấn đề:**
- Dữ liệu Shopify bị **tải 2 lần** (cho fact_orders và fact_order_items)
- Không dọn RAM → máy yếu sẽ **treo**

> **🏆 Bạn thắng** — Kiến trúc phân ca + xử lý từng phần là cách làm **chuyên nghiệp** (production-grade).

---

## 2. 📂 Cấu Trúc Thư Mục

### Bạn ✅ — Đúng chuẩn Python

```python
# File __init__.py giống như "bảng danh sách" cho mỗi thư mục
# Python biết thư mục đó là 1 "gói" (package) có thể import

# Khi cần dùng, chỉ cần:
from extractors.shopify_extractor import ShopifyExtractor
```

### hdangnguyen ❌ — Dùng "mẹo vặt"

```python
# PHẢI thêm đoạn này vào MỖI FILE để Python tìm được code:
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Giống như mỗi lần muốn vào nhà → phải chỉ đường lại từ đầu
# Thay vì gắn biển số nhà 1 lần (= __init__.py)
```

> **🏆 Bạn thắng** — `__init__.py` là cách chuẩn. `sys.path.append` là "hack" tạm bợ.

---

## 3. 🔧 Base Extractor — "Người Đi Chợ Gốc"

### Bạn ✅✅ — Đọc file thông minh, tiết kiệm RAM

```
Cách của bạn (giống đọc sách từng trang):
1. Tải file nén về ổ cứng tạm (không vào RAM)
2. Mở từ từ, đọc TỪNG DÒNG bằng ijson (streaming)
3. Nếu file quá lớn → chia thành chunk 50K dòng/lần

ijson = thư viện đọc JSON kiểu "chảy nước" (streaming)
       Giống đọc sách từng trang, không cần photo cả cuốn
```

### hdangnguyen ❌ — Nạp hết vào RAM

```
Cách của họ (giống photo cả cuốn sách rồi mới đọc):
1. Tải TOÀN BỘ file nén vào RAM          → RAM x1
2. Giải nén TOÀN BỘ trong RAM            → RAM x2
3. Chuyển thành dữ liệu Python trong RAM → RAM x3

File 269MB nén → cần ~3-5GB RAM → MÁY 8GB SẼ CHẾT!
```

> **🏆 Bạn thắng hoàn toàn** — Đây là khác biệt lớn nhất. Máy 8GB của bạn chạy được nhờ `ijson`.

---

## 4. 📐 Mô Hình Dữ Liệu — "Bản Đồ Kho Hàng"

### Bạn — 10 bảng + 3 views

```
📦 BẢNG CHIỀU (Dimension = "Danh mục tra cứu"):
├── dim_customers    → Danh sách khách hàng + phân loại
├── dim_products     → Danh mục sản phẩm
├── dim_locations    → Danh sách cửa hàng/kho     ← hdangnguyen KHÔNG CÓ
├── dim_staff        → Danh sách nhân viên          ← hdangnguyen KHÔNG CÓ
└── dim_date         → Lịch (ngày/tháng/năm/quý)   ← hdangnguyen KHÔNG CÓ

📊 BẢNG SỰ KIỆN (Fact = "Ghi chép giao dịch"):
├── fact_orders           → Tất cả đơn hàng (Shopify + Sapo + Online)
├── fact_order_items      → Chi tiết sản phẩm trong mỗi đơn
├── fact_payments         → Giao dịch thanh toán (PayPal + MoMo + ZaloPay)
├── fact_cart_events      → Hành vi người dùng (xem, thêm giỏ, mua)
└── fact_bank_transactions → Giao dịch ngân hàng Mercury

🔭 VIEWS (= "Cửa sổ nhìn" — kết hợp nhiều bảng sẵn cho Power BI):
├── vw_customer_journey   → Hành trình khách: từ click đầu → mua hàng
├── vw_cashflow_daily     → Dòng tiền hàng ngày: thu - chi = lãi
└── vw_payment_status     → Trạng thái thanh toán: đã trả/chưa/quá hạn
```

### hdangnguyen — 7 bảng, 0 views

```
📦 BẢNG CHIỀU: Chỉ 2 (customers + products)
📊 BẢNG SỰ KIỆN: 5 (giống bạn)
🔭 VIEWS: 0 — phải tự viết SQL trong Power BI
```

**Tại sao quan trọng?**

| Bảng | Tác dụng |
|---|---|
| `dim_date` | Cho phép phân tích theo tuần/quý/năm tài chính/ngày nghỉ lễ. Không có → phải tính thủ công |
| `dim_locations` | Biết đơn hàng từ cửa hàng nào → phân tích doanh thu theo chi nhánh |
| `dim_staff` | Biết nhân viên nào bán → đánh giá hiệu suất nhân viên |
| Views | Power BI **chỉ cần kết nối 1 view** thay vì JOIN 5 bảng → nhanh hơn, ít lỗi hơn |

> **🏆 Bạn thắng** — Mô hình phong phú hơn, hỗ trợ phân tích đa chiều.

---

## 5. 🔑 Surrogate Key — "Mã Số Định Danh"

**Surrogate key** = mã do bạn TỰ TẠO để nhận diện mỗi dòng dữ liệu (giống số CMND).

### Bạn ✅ — Dùng MD5 Hash

```python
# MD5 = "máy xay" biến bất kỳ chuỗi nào thành 16 ký tự duy nhất
# Giống vân tay: 2 người khác nhau → vân tay khác nhau

generate_surrogate_key("order_123", "shopify", "online")
→ "a3f8b2c1e9d04567"   # 16 ký tự hex, CỰC KỲ khó trùng
```

### hdangnguyen ⚠️ — Nối chuỗi bằng dấu `_`

```python
# Chỉ nối các giá trị lại bằng dấu _
create_surrogate_key(df, ["channel", "order_id", "txn_id"], "order_key")
→ "shopify_123_txn_001"   # Dễ đọc nhưng CÓ THỂ TRÙNG

# Ví dụ trùng:
# channel="shopify_123", order_id="txn", txn_id="001"
# → "shopify_123_txn_001"  ← TRÙNG!
```

> **🏆 Bạn thắng** — MD5 hash an toàn cho hàng triệu dòng.

---

## 6. ✅ Kiểm Tra Chất Lượng Dữ Liệu

### Bạn — 4 phương thức riêng biệt + báo cáo tổng hợp

| Phương thức | Làm gì | Ví dụ dễ hiểu |
|---|---|---|
| `check_nulls()` | Tìm ô trống | "Có 500 khách không có email (2.5%)" |
| `check_duplicates()` | Tìm VÀ XÓA dòng trùng | "Tìm thấy 120 đơn trùng → đã xóa" |
| `validate_date_range()` | Kiểm tra ngày hợp lệ | "15 đơn có ngày tương lai → cảnh báo" |
| `validate_amounts()` | Kiểm tra số tiền bất thường | "3 đơn có giá trị > 3σ → có thể là outlier" |

**3σ (sigma)** = quy tắc thống kê: nếu 1 giá trị cách trung bình hơn 3 lần độ lệch chuẩn → **bất thường**. Giống 1 học sinh điểm 10 trong lớp toàn 3-4 điểm → đáng nghi.

**Kết quả được lưu vào `quality_report`** → in ra ở cuối pipeline:
```
Data Quality Issues:
  ⚠ dim_customers.email.nulls: 500
  ⚠ fact_orders.duplicates: 120
```

### hdangnguyen — 1 phương thức khổng lồ, chỉ ghi log

- **1 method `data_quality_check()` dài 280 dòng** → khó bảo trì
- Tìm thấy trùng lặp nhưng **KHÔNG XÓA** — chỉ ghi nhật ký
- Dùng **IQR** thay vì 3σ cho outlier (cũng OK nhưng ít phổ biến)
- Không có báo cáo tổng hợp

> **🏆 Bạn thắng** — Tách riêng từng loại kiểm tra = dễ test, dễ tái sử dụng. Xóa trùng tự động = an toàn hơn.

---

## 7. 🧠 Phân Loại Khách Hàng (RFM)

**RFM** = phương pháp phân loại khách dựa trên 3 yếu tố:
- **R**ecency = Mới mua gần đây không? (càng gần → càng tốt)
- **F**requency = Mua thường xuyên không? (càng nhiều → càng tốt)
- **M**onetary = Chi bao nhiêu tiền? (càng nhiều → càng tốt)

### Bạn — Đơn giản, 4 nhóm

```
Nếu chưa mua lần nào     → "New" (Khách mới)
Nếu mua ≥10 lần hoặc chi ≥50 triệu → "VIP"
Nếu mua ≥3 lần            → "Regular" (Thường xuyên)
Nếu >90 ngày không mua    → "At-risk" (Sắp mất)
```

### hdangnguyen — Phức tạp hơn, 11 nhóm

```
Dùng NTILE(5) = chia khách thành 5 nhóm đều nhau cho mỗi R, F, M
Rồi kết hợp 3 điểm → 11 nhóm: Champions, Loyal, Potential Loyalist,
Promising, New Customer, Need Attention, About To Sleep,
At Risk, Cannot Lose Them, Hibernating, Lost
```

**NTILE(5)** = "chia đều thành 5 phần". Giống xếp hạng học sinh: top 20% = giỏi, 20% tiếp = khá...

**NHƯNG:** Code RFM của hdangnguyen đang bị **commented out** (đã tắt), nên thực tế KHÔNG CHẠY!

> **🏆 hdangnguyen thắng về lý thuyết** — 11 nhóm chi tiết hơn. Nhưng bạn thắng về thực tế vì code của bạn **thực sự chạy**.

---

## 8. 💾 BigQuery Loader — "Người Giao Hàng"

### Bạn ✅✅ — Tự sửa lỗi khi gặp sự cố

```python
# Tình huống: Bạn đổi cách phân vùng (partitioning) bảng
# BigQuery sẽ từ chối: "Bảng cũ không tương thích!"

# Code của bạn TỰ ĐỘNG xử lý:
# 1. Phát hiện lỗi "Incompatible table partitioning"
# 2. Xóa bảng cũ
# 3. Tạo lại bảng mới với cấu hình đúng
# 4. Nạp dữ liệu thành công!

# hdangnguyen: GẶP LỖI NÀY → CRASH → phải sửa tay
```

**Partitioning** (phân vùng) = chia bảng lớn thành nhiều phần theo ngày. Giống chia hồ sơ theo tháng trong tủ → tìm nhanh hơn.

**Clustering** (gom nhóm) = sắp xếp dữ liệu trong mỗi phân vùng. Giống trong mỗi tháng, xếp theo tên khách → tìm còn nhanh hơn nữa.

| Tính năng | Bạn | hdangnguyen |
|---|---|---|
| Tự sửa lỗi partitioning | ✅ | ❌ Crash |
| Tạo 3 Views phân tích | ✅ | ❌ |
| Xem thông tin bảng (`--info`) | ✅ | ❌ |
| Kiểm tra cột tồn tại trước khi partition | ✅ | ❌ |

> **🏆 Bạn thắng** — Auto-retry khi lỗi partition là tính năng **rất thực tế**.

---

## 9. 📝 Ghi Nhật Ký (Logger)

| | Bạn | hdangnguyen |
|---|---|---|
| **File log** | Mỗi ngày 1 file mới (`pipeline_20260422.log`) | 1 file duy nhất mãi mãi |
| **Mã hóa** | UTF-8 (hỗ trợ tiếng Việt) | Không chỉ định (có thể lỗi ký tự) |
| **Thông tin ghi** | Thời gian, mức độ, tên module, **tên hàm + dòng code** | Thời gian, tên, mức độ |
| **Định dạng** | Dùng dấu `\|` ngăn cách (dễ lọc bằng Excel) | Dùng dấu `-` (khó lọc) |

> **🏆 Bạn thắng** — Log xoay vòng theo ngày + ghi tên hàm giúp debug nhanh hơn nhiều.

---

## 10. 🎯 Giao Diện Dòng Lệnh (CLI)

### Bạn ✅ — 4 chế độ chạy

```bash
python main.py --full       # Chạy toàn bộ pipeline
python main.py --extract    # Chỉ tải dữ liệu (kiểm tra GCS)
python main.py --transform  # Tải + biến đổi (không đẩy BigQuery)
python main.py --info       # Xem thông tin bảng BigQuery
```

**Tại sao hay?**
- `--extract`: Kiểm tra GCS có hoạt động không, dữ liệu có đúng format không
- `--transform`: Test logic biến đổi mà không tốn tiền BigQuery
- `--info`: Xem nhanh số dòng, dung lượng các bảng

### hdangnguyen — Không có CLI

```bash
python main.py  # Chạy hết hoặc không chạy gì. Không có lựa chọn.
```

> **🏆 Bạn thắng** — CLI linh hoạt giúp **tiết kiệm thời gian và tiền** khi debug.

---

## 🏆 Bảng Điểm Tổng Kết

| # | Hạng mục | Bạn | hdangnguyen | Ai thắng? |
|---|---|---|---|---|
| 1 | Kiến trúc (phân ca vs liên tục) | ⭐⭐⭐ | ⭐ | 🟢 Bạn |
| 2 | Giao diện dòng lệnh (CLI) | ⭐⭐⭐ | ❌ | 🟢 Bạn |
| 3 | Tiết kiệm RAM (ijson + chunks) | ⭐⭐⭐ | ❌ | 🟢 Bạn |
| 4 | Cấu trúc package (`__init__.py`) | ⭐⭐ | ❌ | 🟢 Bạn |
| 5 | Đặt tên class (PascalCase) | ⭐⭐ | ⭐ | 🟢 Bạn |
| 6 | Type hints + Docstrings | ⭐⭐⭐ | ⭐ | 🟢 Bạn |
| 7 | Mô hình dữ liệu (10 vs 7 bảng) | ⭐⭐⭐ | ⭐⭐ | 🟢 Bạn |
| 8 | Bảng dim_date | ⭐⭐⭐ | ❌ | 🟢 Bạn |
| 9 | Surrogate key (MD5 vs nối chuỗi) | ⭐⭐⭐ | ⭐ | 🟢 Bạn |
| 10 | Kiểm tra chất lượng | ⭐⭐⭐ | ⭐⭐ | 🟢 Bạn |
| 11 | Xử lý trùng lặp (xóa vs chỉ log) | ⭐⭐⭐ | ⭐ | 🟢 Bạn |
| 12 | BigQuery auto-retry | ⭐⭐⭐ | ❌ | 🟢 Bạn |
| 13 | Views phân tích | ⭐⭐⭐ | ❌ | 🟢 Bạn |
| 14 | File cấu hình YAML | ⭐⭐ | ❌ | 🟢 Bạn |
| 15 | Logger (xoay vòng + UTF-8) | ⭐⭐ | ⭐ | 🟢 Bạn |
| 16 | Phân loại khách RFM | ⭐⭐ | ⭐⭐⭐ | 🔵 Họ |
| 17 | Quản lý credentials (.env) | ⭐ | ⭐⭐ | 🔵 Họ |
| | **TỔNG** | **17 thắng** | **2 thắng** | |

---

## 💡 Bạn Có Thể Học Gì Từ hdangnguyen?

> [!TIP]
> **2 điều nên "mượn" về:**
>
> **1. Nâng cấp RFM lên 11 nhóm** — Thay vì 4 nhóm đơn giản, dùng SQL NTILE(5) để chấm điểm R/F/M rồi ghép thành 11 phân khúc chi tiết hơn. Điều này sẽ làm dashboard Customer Journey của bạn **ấn tượng hơn nhiều** khi trình bày.
>
> **2. Chuyển credentials sang .env** — Thay vì viết cứng đường dẫn `C:\Users\Admin\...`, dùng file `.env` để ai khác cũng có thể chạy code mà không cần sửa path.

---

## 📏 So Sánh Kích Thước Code

| File | Bạn | hdangnguyen |
|---|---|---|
| main.py | 100 dòng | 53 dòng |
| base_extractor.py | 147 dòng | 98 dòng |
| base_transformer.py | 238 dòng | 308 dòng |
| dimension_transformer.py | **334 dòng** | 100 dòng |
| fact_transformer.py | **689 dòng** | 462 dòng |
| bigquery_loader.py | **364 dòng** | 218 dòng |
| pipeline_orchestrator.py | **459 dòng** | 428 dòng |
| **Tổng cộng** | **~2,300 dòng** | **~1,400 dòng** |

Code của bạn dài hơn ~65%, nhưng mỗi dòng thêm đều có **giá trị thực**: quản lý RAM, xử lý lỗi, tạo views, báo cáo chất lượng, CLI.
