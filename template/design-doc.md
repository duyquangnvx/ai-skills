<!--
HƯỚNG DẪN SỬ DỤNG TEMPLATE NÀY
================================
Triết lý: "Tài liệu nên ngắn nhất có thể, và dài đến mức cần thiết."

- Các mục đánh dấu (bắt buộc) là phần cốt lõi của mọi design doc, dù ngắn hay dài.
- Các mục đánh dấu (tùy chọn) — xóa thẳng tay nếu không liên quan đến vấn đề bạn
  đang giải quyết. Đừng cố điền cho đủ; một mục để trống hoặc gượng ép thường tệ
  hơn là không có mục đó.
- Dự án nhỏ / thay đổi gia tăng: giữ lại phần "bắt buộc" + may ra 1-2 mục tùy chọn
  liên quan nhất → tài liệu 1-3 trang là hoàn toàn ổn.
- Dự án lớn / phức tạp: cân nhắc thêm hầu hết các mục tùy chọn. Nếu vượt quá
  ~15-20 trang, cân nhắc tách nhỏ vấn đề thay vì nhồi hết vào một doc.
- Xóa khối hướng dẫn này (kể cả comment HTML) trước khi gửi đi review.
-->

# [Tên dự án / tính năng]

## Metadata (bắt buộc)

| | |
|---|---|
| **Tác giả** | |
| **Trạng thái** | Ý tưởng ban đầu / Đang review / Đã duyệt / Đang triển khai / Hoàn thành / Tạm hoãn / Đã thay thế |
| **Người duyệt (approver)** | *(người phải nói "yes" thì mới bắt đầu triển khai — không phải danh sách mọi người được CC)* |
| **Ngày tạo** | |
| **Cập nhật lần cuối** | |

---

## 1. Vấn đề & Mục tiêu (bắt buộc)

**Vấn đề cần giải quyết / cơ hội đang muốn tận dụng là gì?**
*(Nếu mục tiêu khiến người đọc hỏi "ok, nhưng tại sao lại làm việc này?" — hãy trả lời luôn câu hỏi đó ở đây.)*

**Mục tiêu (Goals):**
- ...

**Không phải mục tiêu (Non-goals):** *(tùy chọn, nhưng rất nên có — giúp tránh tranh cãi về scope sau này)*
- ...

> Lưu ý: mục tiêu mô tả *kết quả cần đạt*, không mô tả cách triển khai — phần triển khai để ở mục Thiết kế bên dưới.

---

## 2. Bối cảnh (tùy chọn)

*Thông tin nền mà người đọc cần để đánh giá được thiết kế này — hệ thống hiện tại đang hoạt động ra sao, thuật ngữ cần giải thích, v.v. Bỏ mục này nếu người review đã đủ ngữ cảnh.*

---

## 3. Thiết kế (bắt buộc)

*Đây là phần quan trọng nhất — đừng bỏ qua hay làm mờ nhạt phần này chỉ vì ngại người khác tranh luận chi tiết. "Sai còn hơn mơ hồ": nêu rõ ràng phương án cụ thể, ai/cái gì thực hiện hành động nào, thay vì viết chung chung.*

- Giải pháp đề xuất
- Kiến trúc / luồng dữ liệu / API liên quan (thêm diagram nếu cần)
- Mức độ ràng buộc: đây là hệ thống mới hoàn toàn (greenfield) hay phải tương thích với hệ thống cũ (brownfield)?

---

## 4. Phương án khác đã cân nhắc (tùy chọn, nhưng nên có nếu vấn đề không hiển nhiên)

*Đã có ai ở team/công ty từng thử cách tương tự chưa, và vì sao giải pháp đó không phù hợp? Nếu bạn thấy mình bỏ qua mục này vì "chưa nghĩ đến phương án nào khác" — đó là dấu hiệu nên suy nghĩ kỹ hơn trước khi review.*

| Phương án | Ưu điểm | Nhược điểm | Vì sao không chọn |
|---|---|---|---|
| | | | |

---

## 5. Đánh đổi (Tradeoffs) (tùy chọn)

*Nhược điểm của thiết kế này là gì? Bạn đang đánh đổi điều gì vì tin rằng lợi ích lớn hơn?*

---

## 6. Rủi ro (tùy chọn)

*Điều gì có thể sai sót? Đừng giấu mối lo ngại của chính bạn — nêu ra để người review cùng đánh giá.*

---

## 7. Bảo mật & Quyền riêng tư (tùy chọn — nhưng nên tự hỏi dù chỉ 1 dòng)

- Có dữ liệu/tài sản nào cần bảo vệ, và cần bảo vệ khỏi ai?
- Thiết kế này có thu thập dữ liệu người dùng không?
- Có mở thêm điểm truy cập mới ra bên ngoài không?
- Secrets (API key, credentials...) được lưu trữ và quản lý thế nào?

---

## 8. Phụ thuộc (tùy chọn)

*Bạn cần gì từ các team khác? Hạ tầng, phê duyệt, hỗ trợ từ security/legal/marketing/vận hành...?*

---

## 9. Vận hành & Kế hoạch triển khai (tùy chọn — thường dùng cho dự án lớn)

- Kế hoạch rollout (theo giai đoạn? feature flag? % traffic?)
- Cách theo dõi/giám sát sau khi launch
- Kế hoạch rollback nếu có sự cố
- Timeline / mốc quan trọng (nếu cần track tiến độ)

---

## 10. Câu hỏi mở (tùy chọn)

*Những điều chưa quyết được, nhưng không làm thay đổi bản chất đề xuất nên không cần chặn việc review/duyệt.*

- ...