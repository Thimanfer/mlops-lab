# BÁO CÁO KẾT QUẢ BÀI THỰC HÀNH MLOPS CI/CD
**Học phần**: K3 - CI/CD cho AI Systems: Từ Thí Nghiệm Cục Bộ Đến Triển Khai Liên Tục  
**Học viên thực hiện**: Hồ Văn Thi  
**Source code & Pipeline**: [https://github.com/Thimanfer/mlops-lab](https://github.com/Thimanfer/mlops-lab)  
**Môi trường triển khai**: Google Cloud Platform (GCS & Compute Engine VM)  

---

### 1. Quá trình thực nghiệm & Lựa chọn siêu tham số trên MLflow
Trong giai đoạn thử nghiệm cục bộ, em đã tiến hành chạy 3 thí nghiệm với các cấu hình siêu tham số khác nhau cho mô hình `RandomForestClassifier` và theo dõi toàn bộ qua MLflow:
- **Thí nghiệm 1 (`n_estimators: 100, max_depth: 5`)**: Đạt `Accuracy = 0.5640`, `F1-score = 0.5534`. Do độ sâu cây còn nông nên mô hình chưa học hết được các đặc trưng phức tạp (underfitting).
- **Thí nghiệm 2 (`n_estimators: 200, max_depth: 15`)**: Đạt `Accuracy = 0.6640`, `F1-score = 0.6620`. Hiệu năng được cải thiện rõ rệt khi tăng số cây và độ sâu.
- **Thí nghiệm 3 (`n_estimators: 200, max_depth: 20, min_samples_split: 2`)**: Đạt kết quả tốt nhất với `Accuracy = 0.6840`, `F1-score = 0.6830`.

👉 **Bộ siêu tham số em quyết định chọn**: `n_estimators: 200, max_depth: 20, min_samples_split: 2`.  
**Lý do**: Cấu hình này giúp mô hình bắt trọn các mối quan hệ phi tuyến tính giữa 12 đặc tính lý hóa của rượu vang và mức chất lượng, đồng thời duy trì độ ổn định cao nhất mà không bị overfitting quá mức trên tập dữ liệu ban đầu.

---

### 2. Đánh giá hiệu năng khi Retraining với dữ liệu mới (Continuous Retraining)
Hệ thống CI/CD được thiết lập với một "Eval Gate" (ngưỡng chất lượng tối thiểu $Accuracy \ge 0.70$) trước khi cho phép deploy mô hình lên máy chủ:

| Tiêu chí đánh giá | Phase 1 (2.998 mẫu) | Phase 2 (5.996 mẫu tích lũy) | Mức độ cải thiện |
|---|:---:|:---:|:---:|
| **Accuracy (Độ chính xác)** | `0.6840` | **`0.7600`** | 📈 **Tăng +7.60%** |
| **F1-Score (Weighted)** | `0.6830` | **`0.7580`** | 📈 **Tăng +7.50%** |
| **Hành vi Pipeline CI/CD** | ⛔ *Eval Gate kích hoạt, chặn Deploy* | 🟢 *Vượt qua Eval Gate, Deploy tự động* | Đảm bảo an toàn Production |

**Nhận xét**: Khi em bổ sung thêm 2.998 mẫu từ Phase 2 và đẩy qua DVC, pipeline tự động kích hoạt huấn luyện lại. Dữ liệu dồi dào hơn giúp mô hình nhận diện tốt các mẫu ở phân khúc chất lượng biên, đưa độ chính xác vượt ngưỡng $70\%$ lên $76\%$, đủ điều kiện tự động cập nhật lên VM mà không cần can thiệp thủ công.

---

### 3. Những khó khăn thực tế em đã gặp và cách giải quyết
1. **Rào cản chính sách GCP Organization Constraint**: Project chính trên GCP bị hạn chế quyền tạo khóa Service Account trực tiếp.
   - *Cách em giải quyết*: Em sử dụng Service Account từ project phụ và cấp quyền `roles/storage.objectAdmin` trực tiếp trên bucket của project chính theo đúng nguyên tắc đặc quyền tối thiểu (Principle of Least Privilege).
2. **Xung đột định dạng SSH Key trong GitHub Actions**: Khóa Ed25519 mặc định của OpenSSH gây lỗi parse trên thư viện SSH của GitHub Action runner.
   - *Cách em giải quyết*: Em chủ động sinh cặp khóa định dạng chuẩn RSA 4096 PEM (`mlops_deploy_rsa`), cấu hình quyền `NOPASSWD` trong `/etc/sudoers.d/` trên VM để runner có thể restart systemd service mượt mà.
3. **Độ trễ khởi động khi nạp Model lớn từ GCS**: Lúc service khởi động lại, VM cần vài giây để kéo mô hình mới từ GCS về trước khi API sẵn sàng nhận request, dẫn đến lệnh kiểm tra `/health` ban đầu dễ bị timeout.
   - *Cách em giải quyết*: Em bổ sung cơ chế retry thông minh (`curl --retry 5 --retry-delay 2 --retry-connrefused`) vào workflow deploy, giúp pipeline hoạt động bền bỉ và không bị false-alarm.
