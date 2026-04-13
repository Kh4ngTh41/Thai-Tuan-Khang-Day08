# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Thái Tuấn Khang
**Vai trò trong nhóm:** Eval Owner / Retrieval Owner (Dense)  
**Ngày nộp:** 13/04
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Tôi là Eval Owner và Retrieval Owner tập trung vào Dense retrieval. Tôi chủ yếu làm Sprint 2 (baseline dense), Sprint 4 (evaluation với eval.py), và hỗ trợ Sprint 1 (indexing). Cụ thể, tôi implement `retrieve_dense()` trong `rag_answer.py`, setup ChromaDB với cosine similarity, và viết scorecard trong eval.py với metrics như groundedness, relevance. Tôi quyết định dùng local SentenceTransformer vì privacy và cost. Công việc của tôi kết nối với Tech Lead (hybrid variants) và Documentation Owner (ghi eval results).

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Tôi hiểu rõ hơn về dense retrieval và evaluation metrics. Dense dùng embedding để tìm semantic similarity, tốt cho paraphrase nhưng yếu với exact keywords. Evaluation loop quan trọng — dùng test_questions.json để measure accuracy, groundedness, và abstain rate. Groundedness check nếu answer dựa trên retrieved context, tránh hallucination. Điều này giúp quantify improvements từ variants.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Tôi ngạc nhiên khi dense retrieval score thấp cho queries như "ERR-403-AUTH" — vì embedding không prioritize error codes. Khó khăn nhất là setup eval.py với LLM-as-judge cho groundedness, mất thời gian prompt engineering. Giả thuyết ban đầu: dense luôn outperform sparse, nhưng thực tế sparse tốt hơn cho keyword-heavy queries. Cũng gặp issue với metadata consistency trong chunks.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** SLA xử lý ticket P1 là bao lâu?

**Phân tích:**

Baseline (dense) trả lời đúng với citation từ support/sla-p1-2026.pdf — điểm cao vì retrieval tìm đúng chunk. Không lỗi, generation grounded. Sparse cũng đúng nhưng dense tốt hơn cho semantic match. Hybrid không cải thiện nhiều vì dense đã tốt, nhưng RRF đảm bảo consistency. Lỗi tiềm ẩn ở chunking nếu chunks quá nhỏ miss context, nhưng ở đây OK.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Tôi sẽ thử fine-tune embedding model vì eval cho thấy dense yếu với domain-specific terms như error codes. Cũng implement automated eval với more metrics như faithfulness, vì current scorecard manual.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
