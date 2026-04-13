# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** April 13, 2026  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.20 /5 |
| Answer Relevance | 4.40 /5 |
| Context Recall | 5.00 /5 |
| Completeness | 4.00 /5 |

**Câu hỏi yếu nhất (điểm thấp):**
> q09 (ERR-403-AUTH): faithfulness=1/5, relevance=1/5, completeness=1/5 vì không tìm được thông tin trong corpus (abstain đúng).
> q04 (sản phẩm kỹ thuật số): completeness=4/5 thiếu chi tiết về ngoại lệ.
> q07 (Approval Matrix): faithfulness=4/5, completeness=3/5 vì answer dựa trên access control nhưng không chính xác về "Approval Matrix".

**Giả thuyết nguyên nhân (Error Tree):**
- [x] Retrieval: Dense bỏ lỡ exact keyword/alias (q07, q09)
- [ ] Indexing: Chunking cắt giữa điều khoản
- [ ] Indexing: Metadata thiếu effective_date
- [ ] Retrieval: Top-k quá ít → thiếu evidence
- [ ] Generation: Prompt không đủ grounding
- [ ] Generation: Context quá dài → lost in the middle

---

## Variant 1 (Sprint 3)

**Ngày:** April 13, 2026  
**Biến thay đổi:** hybrid retrieval  
**Lý do chọn biến này:**
> Chọn hybrid vì corpus có cả văn bản chính sách tự nhiên và nhiều keyword/alias quan trọng như "P1", "refund", "Level 3".
> Dense retrieval tốt với ngữ nghĩa nhưng có thể bỏ lỡ exact term; sparse BM25 bổ sung khả năng tìm keyword chính xác.

**Config thay đổi:**
```
retrieval_mode = "hybrid"
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.20/5 | 4.60/5 | +0.40 |
| Answer Relevance | 4.40/5 | 4.60/5 | +0.20 |
| Context Recall | 5.00/5 | 5.00/5 | 0.00 |
| Completeness | 4.00/5 | 4.30/5 | +0.30 |

**Nhận xét:**
> Variant hybrid cải thiện faithfulness (+0.4) và completeness (+0.3) so với baseline dense. Cụ thể:
> - q09 (ERR-403-AUTH): hybrid tìm được thông tin từ access control docs, trả lời đúng về quy trình cấp quyền thay vì abstain.
> - q07 (Approval Matrix): hybrid kết hợp dense + sparse, trả lời chính xác hơn về access control SOP.
> - q04: completeness cải thiện nhờ retrieval tốt hơn.
> Không có câu nào kém hơn, hybrid bổ sung mà không làm giảm chất lượng.

**Kết luận:**
> Variant hybrid tốt hơn baseline đáng kể (+0.23 điểm trung bình). Bằng chứng: cải thiện faithfulness và completeness ở các câu hỏi có keyword/alias, trong khi giữ nguyên context recall hoàn hảo. Hybrid phù hợp với corpus hỗn hợp (policy + technical terms).

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** rerank với cross-encoder  
**Config:**
```
retrieval_mode = "hybrid"
use_rerank = True
# Thêm cross-encoder reranking
```

**Scorecard Variant 2:**
| Metric | Baseline | Variant 1 | Variant 2 | Best |
|--------|----------|-----------|-----------|------|
| Faithfulness | 4.20 | 4.60 | ? | ? |
| Answer Relevance | 4.40 | 4.60 | ? | ? |
| Context Recall | 5.00 | 5.00 | ? | ? |
| Completeness | 4.00 | 4.30 | ? | ? |

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > Retrieval bỏ lỡ exact keyword/alias trong corpus hỗn hợp (policy + technical terms). Dense embedding tốt với ngữ nghĩa nhưng yếu ở keyword matching.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > Hybrid retrieval (dense + sparse) có tác động lớn nhất, cải thiện faithfulness và completeness mà không làm giảm context recall.

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Thử rerank với cross-encoder để lọc top chunks tốt hơn, hoặc query expansion để xử lý alias/tên cũ trong corpus.
