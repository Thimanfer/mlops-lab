# BÁO CÁO TỔNG KẾT BÀI THỰC HÀNH MLOPS CI/CD
**Học viên**: Hồ Văn Thi  
**Repository**: [https://github.com/Thimanfer/mlops-lab](https://github.com/Thimanfer/mlops-lab)  
**Hệ thống triển khai**: Google Cloud Platform (Cloud Storage & Compute Engine)  

---

### 1. Lựa Chọn Siêu Tham Số Dựa Trên Kết Quả MLflow
Trong quá trình thử nghiệm cục bộ tại Bước 1, ba mô hình `RandomForestClassifier` đã được huấn luyện với các bộ tham số khác nhau và ghi nhận kết quả trên MLflow:
- **Thí nghiệm 1** (`n_estimators: 100, max_depth: 5`): `Accuracy = 0.5640 | F1-score = 0.5534` (Mô hình nông, underfitting).
- **Thí nghiệm 2** (`n_estimators: 200, max_depth: 15`): `Accuracy = 0.6640 | F1-score = 0.6620`.
- **Thí nghiệm 3** (`n_estimators: 200, max_depth: 20, min_samples_split: 2`): `Accuracy = 0.6840 | F1-score = 0.6830`.

👉 **Bộ tham số được chọn**: `n_estimators: 200, max_depth: 20, min_samples_split: 2`.  
**Lý do**: Cung cấp độ sâu đủ lớn và số lượng cây phong phú để trích xuất tốt các mối quan hệ phi tuyến giữa 12 đặc trưng hoá học của rượu vang và chất lượng, cho chỉ số Accuracy và F1-score cao nhất trong các lần thử nghiệm.

---

### 2. So Sánh Hiệu Năng Khi Mở Rộng Quy Mô Dữ Liệu (Continuous Retraining)
Khi hệ thống kích hoạt huấn luyện liên tục với tập dữ liệu mới (Phase 2):

| Chỉ số đánh giá | Giai đoạn 1 (2.998 mẫu ban đầu) | Giai đoạn 2 (5.996 mẫu tích lũy) | Mức độ cải thiện |
|---|:---:|:---:|:---:|
| **Accuracy (Độ chính xác)** | `0.6840` | `0.7600` | ⬆ **+7.60%** (Vượt ngưỡng Eval gate $\ge 0.70$) |
| **F1-Score (Weighted)** | `0.6830` | `0.7580` | ⬆ **+7.50%** |
| **Trạng thái Pipeline** | ⛔ *Chặn Deploy tại Eval gate* | 🟢 *Vượt Eval gate $\rightarrow$ Deploy thành công* |

**Nhận xét**: Khi tăng gấp đôi số lượng mẫu huấn luyện, mô hình học được phân phối dữ liệu đa dạng hơn, khắc phục hiện tượng thiếu mẫu ở các mức chất lượng rượu biên, giúp Accuracy tăng vọt từ $68.4\%$ lên $76.0\%$.

---

### 3. Khó Khăn Gặp Phải & Giải Pháp Xử Lý
1. **Chính sách GCP Organization Constraint**: Project chính bị hạn chế tạo Service Account Key trực tiếp.  
   - *Giải pháp*: Tận dụng Service Account liên dự án được cấp quyền `roles/storage.objectAdmin` trên GCS Bucket theo nguyên tắc đặc quyền tối thiểu (Least Privilege).
2. **Định dạng SSH Key cho CI/CD Runner**: Khóa Ed25519 mặc định gặp lỗi parse trên thư viện Go của `appleboy/ssh-action`.  
   - *Giải pháp*: Sử dụng cặp khóa chuẩn RSA 4096 PEM (`mlops_deploy_rsa`), phân quyền sudoers `NOPASSWD` cho user trên VM để restart service mượt mà.
3. **Độ trễ tải mô hình khi khởi động lại API**: Khi service restart, VM cần thời gian tải mô hình dung lượng lớn từ GCS trước khi endpoint `/health` phản hồi.  
   - *Giải pháp*: Thêm cơ chế retry (`curl --retry 5 --retry-delay 2 --retry-connrefused`) vào workflow deploy giúp hệ thống chịu lỗi và triển khai ổn định 100%.
