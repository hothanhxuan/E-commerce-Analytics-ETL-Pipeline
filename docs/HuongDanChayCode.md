# 🚀 Hướng Dẫn Từng Bước: Từ Chạy Code Đến Lên Power BI 📊

Chúc mừng bạn đã hiểu logic vận hành! Bây giờ chúng ta sẽ đi vào phần "Thực hành". Đây là các bước thực tế bạn sẽ làm trên máy tính của mình. 

---

## Bước 1: Chuẩn bị "Nhà máy" (VS Code)

Hiện tại hệ thống thấy bạn đang mở file `main.py` trên VS Code rồi, rất tuyệt!

1. **Mở Terminal (Màn hình gõ lệnh)**: 
   Trên thanh công cụ của VS Code, chọn **Terminal** > **New Terminal** (hoặc bấm tổ hợp phím `Ctrl` + <code>`</code> (nút dưới phím Esc)).
2. **Cài đặt nguyên liệu (Thư viện Python)**:
   Dự án này cần một số công cụ riêng (pandas, cấu hình google cloud...). Trong màn hình Terminal vừa mở ra, bạn gõ lệnh sau rồi ấn Enter:
   ```bash
   pip install -r requirements.txt
   ```
   *Quá trình cài đặt sẽ mất khoảng 1-2 phút. Khi nào nó báo "Successfully installed...", tức là xong.*

3. **Kiểm tra CHÌA KHÓA nhà:**
   Trong code dự án, bạn có sử dụng một chiếc "chìa khóa" (credentials) để cho phép Python vào nhà Google Cloud của bạn. Hãy chắc chắn rằng bạn có file này trong máy tính, tại đúng đường dẫn này:
   📂 `C:\Users\Admin\Desktop\Final Project K41\config\minpyws-e52b3983be71.json`

---

## Bước 2: Nhấn nút "Chạy Nhà Máy" 🏭

1. Vẫn ở trong Terminal của VS Code, gõ lệnh thao tác toàn bộ quy trình ETL (Extract - Transform - Load) rồi nhấn Enter:
   ```bash
   python main.py --full
   ```
2. Bạn sẽ thấy màn hình chạy liên tục các dòng chữ (Log). Code đang báo cáo tiến độ cho bạn:
   - "STARTING FULL ETL PIPELINE"
   - "STEP 1: Creating BigQuery..."
   - "STEP 2: EXTRACTING..."
   - ...
3. Cứ để kệ nó chạy. Tới khi bạn thấy dòng chữ **"PIPELINE COMPLETED SUCCESSFULLY"**, tức là dữ liệu đã được làm sạch và đẩy hết lên kho Cloud!

---

## Bước 3: Lên Google Cloud BigQuery Xem Thành Quả ☁️

BigQuery chính là cái "Kho chứa siêu bự" mà ban nãy nhà máy đẩy đồ lên.

1. Mở trình duyệt web (Chrome/Cốc Cốc) lên. Truy cập vào link: 
   👉 **[https://console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)**
2. Đăng nhập bằng bằng tài khoản Gmail mà bạn đã dùng để tạo cái project có tên `MinPyWS` trước đó.
3. Ở phía trên cùng màn hình (cạnh Google Cloud), đảm bảo bạn đang chọn project tên là **MinPyWS** (hoặc `minpyws`).
4. Ở cột bên trái màn hình (khu vực Explorer), bạn bấm mũi tên sổ xuống theo thứ tự:
   - Sổ tên Project `minpyws`
   - Sổ tên Dataset `techstore_analytics`
5. **Bạn sẽ thấy phép màu!** Tất cả các bảng dữ liệu: `dim_customers`, `fact_orders`, v...v.. đã nằm gọn gàng ở đây.
6. Muốn xem dữ liệu bên trong? Bấm click vào tên một bảng (ví dụ: `dim_customers`), nhìn sang ô ở giữa, chọn tab **PREVIEW** (Xem trước) là thấy bảng cột dữ liệu ngập tràn.

---

## Bước 4: Chuyển dữ liệu qua PowerBI để vẽ Biểu Đồ 🎨

Giờ chúng ta sẽ đưa cái kho dữ liệu BigQuery kia xuống PowerBI.

1. Bật phần mềm **Power BI Desktop** trong máy tính lên.
2. Tại màn hình chính, bấm vào nút **Get Data** (Lấy dữ liệu).
3. Vì BigQuery nằm mục sâu bên trong, bạn chọn **More...** (Nhiều hơn).
4. Tại ô tìm kiếm (Search), bạn gõ chữ **Google BigQuery**, chọn nó và bấm **Connect** (Kết nối).
5. **Đăng nhập:** PowerBI sẽ hiện cửa sổ yêu cầu đăng nhập. Bạn hãy:
   - Đăng nhập bằng đúng cái tài khoản Gmail sử dụng ở Bước 3.
   - Nhấn "Allow" (Cấp quyền) cho PowerBI tự do truy cập BigQuery.
6. **Màn hình Navigator hiện ra:** 
   - Bạn mở lần lượt `minpyws` > `techstore_analytics`.
   - Tích chọn (☑️) vào 3 cái Views đã được chuẩn bị sẵn, bao gồm:
      - ☑️ `vw_cashflow_daily`
      - ☑️ `vw_customer_journey` 
      - ☑️ `vw_payment_status`
   - Bấm nút **Load** (Tải).

> [!TIP]
> Bạn chỉ nên lấy 3 cái `vw_...` (Views) vào Power BI. Vì Views là những bảng đã được sắp xếp, tổng hợp sẵn chuyên dùng để lên biểu đồ ở dự án này.

🎉 **XONG:** Giờ 3 bảng dữ liệu đã nằm gọng gàng ở khung bên phải của PowerBI. Bạn thoải mái kéo/thả ra màn hình chính, chọn màu sắc để vẽ ra 3 Dashboard đỉnh cao! 
