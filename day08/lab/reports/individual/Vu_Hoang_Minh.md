# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Vũ Hoàng Minh
**Vai trò trong nhóm:** Tech Lead / Retrieval Owner (Hybrid)  
**Ngày nộp:** 13/04
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Mô tả cụ thể phần bạn đóng góp vào pipeline:
> - Sprint nào bạn chủ yếu làm?
> - Cụ thể bạn implement hoặc quyết định điều gì?
> - Công việc của bạn kết nối với phần của người khác như thế nào?

Tôi là Tech Lead và Retrieval Owner tập trung vào Hybrid retrieval. Tôi chủ yếu làm Sprint 1 (indexing), Sprint 2 (baseline dense retrieval), Sprint 3 (hybrid retrieval với RRF), và Sprint 4 (evaluation và documentation). Cụ thể, tôi implement `get_embedding()`, `build_index()` trong `index.py`, `retrieve_dense()`, `retrieve_sparse()`, `retrieve_hybrid()` trong `rag_answer.py`, và `compare_retrieval_strategies()`. Tôi quyết định dùng SentenceTransformer local cho embedding, BM25 cho sparse, và RRF cho hybrid vì nó balance precision và recall. Công việc của tôi kết nối với Eval Owner (đánh giá variants) và Documentation Owner (ghi lại tuning decisions).

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Chọn 1-2 concept từ bài học mà bạn thực sự hiểu rõ hơn sau khi làm lab.
> Ví dụ: chunking, hybrid retrieval, grounded prompt, evaluation loop.
> Giải thích bằng ngôn ngữ của bạn — không copy từ slide.

Tôi hiểu rõ hơn về hybrid retrieval và RRF. Hybrid kết hợp dense (semantic) và sparse (keyword) để cover cả paraphrase queries và exact terms. RRF rank fusion đơn giản nhưng hiệu quả, không cần tuning weights phức tạp. Nó giúp retrieval robust hơn, đặc biệt cho queries đa dạng như trong test_questions.json. Grounded prompt cũng quan trọng — ép LLM cite sources và abstain nếu thiếu evidence, tránh hallucination.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Điều gì xảy ra không đúng kỳ vọng?
> Lỗi nào mất nhiều thời gian debug nhất?
> Giả thuyết ban đầu của bạn là gì và thực tế ra sao?

Tôi ngạc nhiên khi dense retrieval trả lời "I do not know" cho "ERR-403-AUTH" nhưng sparse/hybrid trả lời được — vì embedding không capture exact error codes tốt. Khó khăn nhất là debug chunking và metadata — ban đầu chunks thiếu source, dẫn đến citations sai. Giả thuyết ban đầu: dense luôn tốt hơn sparse, nhưng thực tế hybrid tốt nhất cho balance. Cũng gặp issue với OpenAI API rate limits khi test nhiều.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

> Chọn 1 câu hỏi trong test_questions.json mà nhóm bạn thấy thú vị.
> Phân tích:
> - Baseline trả lời đúng hay sai? Điểm như thế nào?
> - Lỗi nằm ở đâu: indexing / retrieval / generation?
> - Variant có cải thiện không? Tại sao có/không?

**Câu hỏi:** ERR-403-AUTH là lỗi gì và cách xử lý?

**Phân tích:**

Baseline (dense) trả lời "I do not know" — sai, điểm thấp vì không grounded. Lỗi ở retrieval: embedding không match error code, chunks retrieved không chứa "ERR-403-AUTH". Sparse trả lời đúng với citation từ it/access-control-sop.md — điểm cao vì keyword match. Hybrid cũng đúng, cải thiện từ dense bằng RRF. Generation OK khi có context, nhưng abstain khi thiếu. Variant (hybrid) cải thiện baseline vì kết hợp strengths, nhưng không fix nếu docs thiếu info.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> 1-2 cải tiến cụ thể bạn muốn thử.
> Không phải "làm tốt hơn chung chung" mà phải là:
> "Tôi sẽ thử X vì kết quả eval cho thấy Y."

Tôi sẽ thử rerank với cross-encoder vì eval cho thấy top-3 chunks đôi khi có noise, dẫn đến answers kém. Cũng thử query expansion cho queries mơ hồ như "ERR-403-AUTH là lỗi gì?", vì retrieval hiện tại yếu với insufficient context.

---

*Lưu file này với tên: `reports/individual/[ten_ban].md`*
*Ví dụ: `reports/individual/nguyen_van_a.md`*
