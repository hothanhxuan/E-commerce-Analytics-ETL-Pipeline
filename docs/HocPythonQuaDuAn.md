# 🐍 Học Python Qua Dự Án TechStore — Từ Số 0

> [!NOTE]
> Bài này giải thích Python **từ cơ bản nhất**, dùng chính code trong dự án của bạn làm ví dụ.
> Mỗi khái niệm sẽ đi kèm: **ví dụ đời thường** → **code thật** → **giải thích từng dòng**.

---

## 📚 Mục Lục

1. [Biến (Variable)](#-1-biến-variable--cái-hộp-đựng-đồ)
2. [Hàm (Function)](#-2-hàm-function--công-thức-nấu-ăn)
3. [Import](#-3-import--mượn-đồ-hàng-xóm)
4. [Class & Object (OOP)](#-4-class--object--bản-thiết-kế--sản-phẩm)
5. [Kế thừa (Inheritance)](#-5-kế-thừa-inheritance--con-giống-cha-mẹ)
6. [`__init__` và `self`](#-6-__init__-và-self--khai-sinh--chứng-minh-thư)
7. [List & Dictionary](#-7-list--dictionary--danh-sách--từ-điển)
8. [Vòng lặp (For loop)](#-8-vòng-lặp-for-loop--lặp-đi-lặp-lại)
9. [If/Else](#-9-ifelse--nếuthì)
10. [Try/Except](#-10-tryexcept--thử-nếu-lỗi-thì)
11. [f-string](#-11-f-string--chèn-biến-vào-chữ)
12. [Đọc lại toàn bộ flow](#-12-ghép-tất-cả-lại--đọc-code-thật)

---

## 📦 1. Biến (Variable) — "Cái hộp đựng đồ"

### Đời thường:
Bạn có một **cái hộp**, bạn dán nhãn "tên" lên hộp, rồi bỏ đồ vào.

### Code:
```python
ten = "Minh"           # Hộp tên "ten", bên trong chứa chữ "Minh"
tuoi = 25              # Hộp tên "tuoi", bên trong chứa số 25
bucket_name = "minpy"  # Hộp tên "bucket_name", chứa chữ "minpy"
```

### Trong dự án (file [base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L17-L19)):
```python
self.client = storage.Client(credentials=credentials)  # Hộp "client" chứa kết nối đến Google
self.bucket = self.client.bucket(bucket_name)           # Hộp "bucket" chứa cái xô dữ liệu
self.bucket_name = bucket_name                          # Hộp "bucket_name" chứa tên xô = "minpy"
```

> **Quy tắc đặt tên:** dùng chữ thường, các từ nối bằng dấu `_`. Ví dụ: `bucket_name`, `all_data`, `raw_data`.

---

## 🍳 2. Hàm (Function) — "Công thức nấu ăn"

### Đời thường:
Công thức nấu **trứng chiên**:
1. Cho dầu vào chảo
2. Đập trứng
3. Chiên đến vàng
4. **Trả ra:** đĩa trứng chiên

Mỗi lần muốn ăn → chỉ cần gọi "nấu trứng chiên" → không cần nhớ lại từng bước!

### Code cơ bản:
```python
def nau_trung_chien(so_trung):     # "def" = định nghĩa công thức
    """Nấu trứng chiên"""          # Mô tả công thức (docstring)
    cho_dau_vao_chao()             # Bước 1
    dap_trung(so_trung)            # Bước 2
    chien_den_vang()               # Bước 3
    return dia_trung               # Trả ra kết quả

# Sử dụng:
bua_sang = nau_trung_chien(2)      # Gọi công thức, nấu 2 trứng
```

### Trong dự án (file [base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L22-L34)):
```python
def extract_json_gzip(self, prefix_path):
    """Extract file json.gz from prefix path in GCS"""

    # Bước 1: Tìm file trong xô GCS
    blob = self.bucket.blob(prefix_path)

    # Bước 2: Tải file nén về (download)
    compressed_data = blob.download_as_bytes()

    # Bước 3: Giải nén (unzip)
    decompressed_data = gzip.decompress(compressed_data)

    # Bước 4: Chuyển từ text thành dữ liệu Python có thể đọc
    data = json.loads(decompressed_data.decode('utf-8'))

    # Bước 5: TRẢ VỀ dữ liệu
    return data
```

> **Giải thích từng dòng:**
> | Dòng | Giống như... |
> |------|-------------|
> | `blob = self.bucket.blob(prefix_path)` | Mở tủ lạnh, tìm hộp đồ ở vị trí `prefix_path` |
> | `compressed_data = blob.download_as_bytes()` | Lấy hộp đồ ra (còn đóng hộp chân không) |
> | `decompressed_data = gzip.decompress(...)` | Mở hộp chân không ra |
> | `data = json.loads(...)` | Đọc hiểu nội dung bên trong |
> | `return data` | Đưa đồ cho người gọi |

---

## 📬 3. Import — "Mượn đồ hàng xóm"

### Đời thường:
Bạn muốn nấu ăn nhưng không có máy xay → **mượn** máy xay nhà hàng xóm.

### Code:
```python
# Mượn "máy giải nén" từ thư viện gzip
import gzip

# Mượn "máy đọc JSON" từ thư viện json
import json

# Mượn "kết nối Google Cloud" từ thư viện google
from google.cloud import storage

# Mượn "công thức ghi nhật ký" từ file utils/logger.py trong chính dự án
from utils.logger import setup_logger
```

### Trong dự án ([base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L1-L6) dòng 1-6):
```python
from google.cloud import storage                # Mượn: công cụ kết nối Google Cloud Storage
from google.oauth2 import service_account        # Mượn: công cụ xác thực (như CMT để vào nhà Google)
import gzip                                      # Mượn: máy giải nén file .gz
import json                                      # Mượn: máy đọc file JSON
from utils.logger import setup_logger            # Mượn: máy ghi nhật ký từ file khác trong dự án
```

> **2 kiểu import:**
> - `import gzip` → Mượn **cả hộp đồ** → dùng: `gzip.decompress(...)`
> - `from utils.logger import setup_logger` → Chỉ mượn **1 món** từ hộp → dùng: `setup_logger(...)`

---

## 🏗️ 4. Class & Object — "Bản thiết kế" & "Sản phẩm"

### Đời thường:
- **Class** = **Bản thiết kế** xe hơi (vẽ trên giấy)
- **Object** = **Chiếc xe thật** được sản xuất từ bản thiết kế đó

Từ 1 bản thiết kế → sản xuất ra nhiều chiếc xe khác nhau (xe đỏ, xe xanh...)

### Code cơ bản:
```python
# BẢN THIẾT KẾ (class)
class XeHoi:
    def __init__(self, mau_sac):
        self.mau_sac = mau_sac       # Mỗi xe có 1 màu riêng

    def chay(self):
        print(f"Xe {self.mau_sac} đang chạy!")

# SẢN XUẤT xe thật (tạo object)
xe1 = XeHoi("đỏ")      # Xe thứ 1 màu đỏ
xe2 = XeHoi("xanh")     # Xe thứ 2 màu xanh

xe1.chay()   # In ra: "Xe đỏ đang chạy!"
xe2.chay()   # In ra: "Xe xanh đang chạy!"
```

### Trong dự án ([base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L9-L10)):
```python
# BẢN THIẾT KẾ "Người đi chợ"
class BaseExtractor:
    """This class is base class for all extractor"""
    ...
```
Và khi sử dụng (trong [pipeline_orchestrator.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/orchestration/pipeline_orchestrator.py#L33)):
```python
# SẢN XUẤT "người đi chợ Shopify" từ bản thiết kế
self.shopify_extractor = ShopifyExtractor()
```

---

## 👨‍👩‍👧 5. Kế thừa (Inheritance) — "Con giống cha mẹ"

### Đời thường:
- **Cha/Mẹ** biết: đi bộ, ăn, ngủ
- **Con** thừa hưởng tất cả kỹ năng của cha mẹ + biết thêm: chơi game

→ Con **không cần học lại** đi bộ, ăn, ngủ. Con **chỉ cần học thêm** chơi game!

### Code:
```python
# CHA (BaseExtractor) biết:
#   - Kết nối GCS          (__init__)
#   - Tải 1 file           (extract_json_gzip)
#   - Tải nhiều file batch  (extract_json_gzip_batches)
#   - Liệt kê file         (list_blobs)

class BaseExtractor:
    def __init__(self, bucket_name):
        # Kết nối GCS...
    
    def extract_json_gzip(self, prefix_path):
        # Tải 1 file...
    
    def extract_json_gzip_batches(self, prefix, pattern, batch_count):
        # Tải nhiều file...
```

```python
# CON (ShopifyExtractor) thừa hưởng hết kỹ năng của CHA
# + biết thêm: cách lấy đơn hàng Shopify cụ thể

class ShopifyExtractor(BaseExtractor):    # ← "(BaseExtractor)" = con của BaseExtractor
    def __init__(self, bucket_name="minpy"):
        super().__init__(bucket_name)      # ← "super()" = gọi cha, bảo cha setup giùm

    def extract_orders(self):
        # CHỈ CẦN GỌI kỹ năng CỦA CHA, không cần viết lại!
        orders = self.extract_json_gzip_batches(
            prefix="shopify/",
            pattern="orders_batch_{}.json.gz",
            batch_count=5
        )
        return orders
```

### Tại sao làm vậy?
> Vì `PaymentExtractor`, `SapoExtractor`, `TrackingExtractor`... đều cần kết nối GCS và tải file.
> Thay vì **copy-paste** cùng 1 đoạn code vào 4 file → viết **1 lần ở cha** → 4 đứa con tự thừa hưởng!

```
BaseExtractor (CHA)
    ├── ShopifyExtractor (CON 1)    ← biết thêm: lấy đơn Shopify
    ├── SapoExtractor (CON 2)       ← biết thêm: lấy đơn Sapo
    ├── PaymentExtractor (CON 3)    ← biết thêm: lấy PayPal, MoMo, ZaloPay
    └── TrackingExtractor (CON 4)   ← biết thêm: lấy dữ liệu theo dõi
```

---

## 🪪 6. `__init__` và `self` — "Khai sinh" & "Chứng minh thư"

### `__init__` = Khai sinh

Khi một **em bé được sinh ra**, phải khai sinh: đặt tên, ghi ngày sinh, v.v.

Khi một **object được tạo ra**, Python tự động gọi `__init__` để "khai sinh" cho nó.

```python
class BaseExtractor:
    def __init__(self, bucket_name):        # ← Giấy khai sinh
        self.bucket_name = bucket_name      # ← Ghi tên xô
        self.client = storage.Client(...)   # ← Tạo kết nối
        self.logger = setup_logger(...)     # ← Tạo sổ nhật ký
```

Khi bạn viết:
```python
extractor = BaseExtractor("minpy")
```
Python tự gọi `__init__` và truyền `bucket_name = "minpy"`.

### `self` = "Tôi" / Chứng minh thư

`self` là cách object **nói về chính mình**: "**CÁI NÀY** là của tôi".

```python
class NguoiDiCho:
    def __init__(self, ten):
        self.ten = ten           # TÔI tên là...
        self.gio_hang = []       # GIỎ HÀNG CỦA TÔI đang rỗng
    
    def mua_do(self, mon):
        self.gio_hang.append(mon)  # Bỏ đồ vào GIỎ HÀNG CỦA TÔI

an = NguoiDiCho("An")       # An có giỏ hàng riêng
binh = NguoiDiCho("Bình")   # Bình có giỏ hàng riêng

an.mua_do("trứng")          # An mua trứng → vào giỏ CỦA AN
binh.mua_do("sữa")          # Bình mua sữa → vào giỏ CỦA BÌNH
```

> `self.bucket` = "cái xô **CỦA TÔI**"
> `self.logger` = "sổ nhật ký **CỦA TÔI**"

---

## 📋 7. List & Dictionary — "Danh sách" & "Từ điển"

### List = Danh sách có thứ tự (dùng `[]`)
```python
# Danh sách đi chợ
do_can_mua = ["trứng", "sữa", "bánh mì"]

# Truy cập: bắt đầu từ 0
do_can_mua[0]   # → "trứng"
do_can_mua[1]   # → "sữa"
```

Trong dự án:
```python
all_data = []                     # Danh sách rỗng
all_data.extend(batch_data)       # Thêm nhiều món vào danh sách
```

### Dictionary = Từ điển tra cứu (dùng `{}`)
```python
# Như cuốn danh bạ: tên → số điện thoại
danh_ba = {
    "An": "0911111111",
    "Bình": "0922222222"
}

danh_ba["An"]   # → "0911111111"
```

Trong dự án ([pipeline_orchestrator.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/orchestration/pipeline_orchestrator.py#L44-L46)):
```python
# Từ điển: tên nguồn → dữ liệu thô
self.raw_data = {}

# Lưu dữ liệu vào từ điển
self.raw_data["shopify_orders"] = shopify_extractor.extract_orders()
self.raw_data["customers"] = sapo_extractor.extract_customers()

# Tra cứu lại
self.raw_data["shopify_orders"]   # → danh sách đơn hàng Shopify
```

> **Phân biệt:**
> | | List `[]` | Dictionary `{}` |
> |---|---|---|
> | Giống | Danh sách đi chợ | Danh bạ điện thoại |
> | Truy cập | Theo **số thứ tự**: `[0], [1], [2]` | Theo **tên**: `["shopify_orders"]` |
> | Dùng khi | Cần **liệt kê** nhiều thứ giống nhau | Cần **tra cứu** theo tên |

---

## 🔄 8. Vòng lặp (For loop) — "Lặp đi lặp lại"

### Đời thường:
Bạn có 5 hộp quà. Bạn **mở từng hộp một**: hộp 1, hộp 2, hộp 3, hộp 4, hộp 5.

### Code cơ bản:
```python
for i in range(5):     # Lặp 5 lần: i = 0, 1, 2, 3, 4
    print(f"Mở hộp {i}")
```

### Trong dự án ([base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L48-L58)):
```python
def extract_json_gzip_batches(self, prefix, pattern, batch_count):
    all_data = []                                   # Giỏ hàng rỗng
    for i in range(batch_count):                    # Lặp qua từng batch
        file_path = f"{prefix}{pattern.format(i)}"  # Tên file: shopify/orders_batch_0.json.gz
        batch_data = self.extract_json_gzip(file_path)  # Tải file này
        all_data.extend(batch_data)                 # Đổ vào giỏ hàng chung
    return all_data                                 # Trả giỏ hàng đầy
```

Giống như:
```
batch_count = 5, vậy lặp 5 lần:
  Lần 0: Tải file shopify/orders_batch_0.json.gz → đổ vào giỏ
  Lần 1: Tải file shopify/orders_batch_1.json.gz → đổ vào giỏ
  Lần 2: Tải file shopify/orders_batch_2.json.gz → đổ vào giỏ
  Lần 3: Tải file shopify/orders_batch_3.json.gz → đổ vào giỏ
  Lần 4: Tải file shopify/orders_batch_4.json.gz → đổ vào giỏ
→ Trả về giỏ hàng có ~200,000 đơn hàng!
```

Một ví dụ khác, lặp qua dictionary ([pipeline_orchestrator.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/orchestration/pipeline_orchestrator.py#L234-L244)):
```python
dim_configs = {
    "dim_customers": {"partition_field": "created_at"},
    "dim_products": {},
    "dim_locations": {},
}

for table_name, config in dim_configs.items():   # Lặp qua từng cặp (tên, cấu hình)
    df = self.transformed.get(table_name)         # Lấy dữ liệu của bảng đó
    self.loader.load_dataframe(table_name=table_name, df=df)  # Đưa lên BigQuery
```

---

## ❓ 9. If/Else — "Nếu...thì..."

### Đời thường:
- **Nếu** trời mưa → mang ô
- **Nếu không** → mang kính mát

### Code:
```python
if troi_mua:
    mang_o()
else:
    mang_kinh_mat()
```

### Trong dự án ([base_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/base_extractor.py#L53-L56)):
```python
if isinstance(batch_data, list):      # NẾU dữ liệu là danh sách
    all_data.extend(batch_data)       # → Đổ tất cả vào giỏ
else:                                 # NẾU KHÔNG (chỉ là 1 đối tượng)
    all_data.append(batch_data)       # → Bỏ nguyên 1 cục vào giỏ
```

Và trong [main.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/main.py#L52-L65):
```python
if args.full:                         # NẾU user gõ --full
    orchestrator.run_full_pipeline()  # → Chạy toàn bộ nhà máy

elif args.extract:                    # NẾU KHÔNG, mà gõ --extract
    orchestrator.run_extract_only()   # → Chỉ đi chợ

elif args.transform:                  # NẾU KHÔNG, mà gõ --transform
    orchestrator.run_transform_only() # → Đi chợ + nấu nướng
```

---

## 🛡️ 10. Try/Except — "Thử, nếu lỗi thì..."

### Đời thường:
- **Thử** nấu ăn
- **Nếu cháy** → tắt bếp, gọi cứu hỏa

### Code:
```python
try:
    nau_an()                         # THỬ nấu ăn
except Exception as e:               # NẾU BỊ LỖI (e = mô tả lỗi)
    print(f"Ôi, lỗi rồi: {e}")      # → Thông báo lỗi
```

### Trong dự án ([pipeline_orchestrator.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/orchestration/pipeline_orchestrator.py#L63-L94)):
```python
try:
    self._step_create_dataset()          # THỬ chạy bước 1
    self._step_extract()                 # THỬ chạy bước 2
    self._step_transform_dimensions()    # THỬ chạy bước 3
    # ...
except Exception as e:
    self.logger.error(f"PIPELINE FAILED: {e}")  # Ghi nhật ký lỗi
    raise                                        # Ném lỗi ra ngoài
```

> Nếu **bất kỳ bước nào** bị lỗi → Python nhảy thẳng xuống `except` → ghi nhật ký → dừng.

---

## 📝 11. f-string — "Chèn biến vào chữ"

### Đời thường:
"Xin chào, tôi tên là **[tên]**, tôi **[tuổi]** tuổi"

### Code:
```python
ten = "Minh"
tuoi = 25

# Kiểu cũ (khó đọc):
print("Xin chào, tôi tên là " + ten + ", tôi " + str(tuoi) + " tuổi")

# Kiểu mới - f-string (dễ đọc!):
print(f"Xin chào, tôi tên là {ten}, tôi {tuoi} tuổi")
# → "Xin chào, tôi tên là Minh, tôi 25 tuổi"
```

### Trong dự án:
```python
self.logger.info(f"Extracting: gs://{self.bucket_name}/{prefix_path}")
# → "Extracting: gs://minpy/shopify/orders_batch_0.json.gz"

self.logger.info(f"Extracted {len(data)} records from {prefix_path}")
# → "Extracted 50000 records from shopify/orders_batch_0.json.gz"
```

> **Bí kíp:** `f"..."` + `{biến}` = chèn giá trị biến vào chuỗi!

---

## 🧩 12. Ghép tất cả lại — Đọc code thật!

Bây giờ hãy đọc lại [shopify_extractor.py](file:///c:/Users/Admin/Desktop/Final%20Project%20K41/extractors/shopify_extractor.py) — file nhỏ nhất — với kiến thức mới:

```python
# === DÒNG 1-4: MÔ TẢ FILE ===
"""
Shopify Extractor - Extracts order data from Shopify online store.
Handles batched order files from gs://minpy/shopify/
"""
# ↑ Đoạn văn mô tả file này làm gì (không ảnh hưởng code)

# === DÒNG 6: MƯỢN ĐỒ ===
from extractors.base_extractor import BaseExtractor
# ↑ Mượn bản thiết kế "BaseExtractor" từ file base_extractor.py

# === DÒNG 9: BẢN THIẾT KẾ MỚI ===
class ShopifyExtractor(BaseExtractor):
# ↑ Tạo bản thiết kế mới tên "ShopifyExtractor"
# ↑ "(BaseExtractor)" = CON của BaseExtractor = thừa hưởng mọi kỹ năng

    """Extractor for Shopify e-commerce platform data."""
    # ↑ Mô tả class

    # === DÒNG 12-14: KHAI SINH ===
    def __init__(self, bucket_name: str = "minpy"):
    # ↑ Khi tạo ShopifyExtractor → chạy đoạn này
    # ↑ bucket_name = "minpy" là giá trị mặc định (nếu không truyền gì)

        """Initialize Shopify extractor."""
        super().__init__(bucket_name)
        # ↑ Gọi CHA (BaseExtractor) setup giùm:
        #   - Kết nối Google Cloud
        #   - Lấy xô "minpy"
        #   - Tạo sổ nhật ký

    # === DÒNG 16-30: CÔNG THỨC ĐI CHỢ SHOPIFY ===
    def extract_orders(self) -> list:
    # ↑ Định nghĩa hàm "lấy đơn hàng"
    # ↑ "-> list" = hàm này sẽ trả về một danh sách

        """Extract all Shopify order batches."""

        self.logger.info("Starting Shopify orders extraction...")
        # ↑ Ghi nhật ký: "Bắt đầu lấy đơn Shopify..."

        orders = self.extract_json_gzip_batches(
        # ↑ Gọi kỹ năng CỦA CHA (vì ShopifyExtractor không có hàm này
        #   → Python tự tìm lên CHA BaseExtractor → thấy → chạy!)

            prefix="shopify/",
            # ↑ Tìm trong thư mục "shopify/" trên GCS

            pattern="orders_batch_{}.json.gz",
            # ↑ Tên file theo mẫu: orders_batch_0, orders_batch_1...

            batch_count=5
            # ↑ Có 5 file batch (0, 1, 2, 3, 4)
        )

        self.logger.info(f"Shopify extraction complete: {len(orders)} total orders")
        # ↑ Ghi nhật ký: "Lấy xong: 200,000 đơn"

        return orders
        # ↑ TRẢ VỀ danh sách đơn hàng cho người gọi
```

---

## 🎯 Cheat Sheet — Bảng tóm tắt nhanh

| Ký hiệu | Nghĩa | Ví dụ |
|----------|-------|-------|
| `def` | Định nghĩa hàm | `def extract_orders(self):` |
| `class` | Định nghĩa bản thiết kế | `class ShopifyExtractor:` |
| `self` | "Của tôi" | `self.bucket_name` |
| `__init__` | Khai sinh object | `def __init__(self, name):` |
| `super()` | Gọi cha | `super().__init__(...)` |
| `return` | Trả kết quả | `return data` |
| `import` | Mượn đồ | `import json` |
| `from...import` | Mượn 1 món cụ thể | `from utils.logger import setup_logger` |
| `[]` | List (danh sách) | `all_data = []` |
| `{}` | Dictionary (từ điển) | `raw_data = {}` |
| `for...in` | Lặp | `for i in range(5):` |
| `if...elif...else` | Nếu ... thì | `if args.full:` |
| `try...except` | Thử, bắt lỗi | `try: ... except: ...` |
| `f"...{var}"` | Chèn biến vào chữ | `f"Hello {name}"` |
| `"""..."""` | Docstring (mô tả) | `"""This function..."""` |
| `#` | Ghi chú (bị bỏ qua) | `# This is a comment` |

---

## 🗺️ Tóm tắt: Luồng chạy toàn bộ dự án

```
1. User gõ: python main.py --full

2. main.py đọc "--full" → tạo PipelineOrchestrator

3. PipelineOrchestrator.__init__() → "Khai sinh" quản lý nhà máy
   → Tạo ShopifyExtractor, SapoExtractor, PaymentExtractor...
   → Tạo DimensionTransformer, FactTransformer
   → Tạo BigQueryLoader

4. run_full_pipeline() → Bắt đầu chạy nhà máy:
   
   Bước 1: _step_create_dataset()
           → Tạo "phòng" trong BigQuery để chứa dữ liệu
   
   Bước 2: _step_extract()
           → shopify_extractor.extract_orders()      → 200K đơn Shopify
           → sapo_extractor.extract_customers()       → 2M khách hàng
           → payment_extractor.extract_paypal()       → 300 giao dịch PayPal
           → ... (tất cả dữ liệu thô được lưu vào self.raw_data)
   
   Bước 3: _step_transform_dimensions()
           → Dữ liệu thô → dọn dẹp → tạo 5 bảng dimension
   
   Bước 4: _step_load_dimensions()
           → Đưa 5 bảng dimension lên BigQuery
   
   Bước 5: _step_transform_facts()
           → Dữ liệu thô → dọn dẹp → tạo 5 bảng fact
   
   Bước 6: _step_load_facts()
           → Đưa 5 bảng fact lên BigQuery
   
   Bước 7: _step_update_aggregates()
           → Cập nhật thông tin tổng hợp khách hàng
   
   Bước 8: _step_create_views()
           → Tạo 3 "cửa sổ nhìn" phục vụ Power BI

5. Power BI kết nối BigQuery → Hiển thị 3 dashboard đẹp! 🎉
```

> [!TIP]
> **Mẹo đọc code:** Đừng cố hiểu hết 1 lần. Hãy bắt đầu từ `main.py` → theo dòng chạy → khi gặp hàm lạ → nhảy sang file tương ứng đọc hàm đó → quay lại. Giống như đọc truyện trinh thám, theo từng manh mối! 🔍
