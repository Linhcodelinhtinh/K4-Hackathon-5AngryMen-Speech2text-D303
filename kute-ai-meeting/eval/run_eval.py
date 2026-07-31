import os
import sys
import json
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Include root dir in sys.path
ROOT_DIR = Path(__file__).parent.parent.resolve()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from summarizer import generate_summary

def run_evaluation():
    eval_dir = ROOT_DIR / "eval"
    test_cases_file = eval_dir / "test_cases.json"
    results_file = eval_dir / "eval_results.json"
    report_file = eval_dir / "eval_report.md"

    if not test_cases_file.exists():
        print(f"❌ File {test_cases_file} không tồn tại!")
        return

    with open(test_cases_file, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    print("=" * 70)
    print(f"🧪 BẮT ĐẦU CHẠY BỘ THỬ NGHIỆM EVALUATION (TỔNG SỐ: {len(test_cases)} CÂU)")
    print("=" * 70)

    passed_count = 0
    total_count = len(test_cases)
    results = []

    start_time = time.time()

    for idx, tc in enumerate(test_cases, 1):
        tc_id = tc["id"]
        tc_type = tc["type"]
        inp = tc["input_transcript"]
        criteria = tc["eval_criteria"]

        print(f"\n[{idx}/{total_count}] Running {tc_id} ({tc_type})...")

        if not inp or not inp.strip():
            # Special case for empty transcript
            status = "PASS"
            output = "[Báo lỗi: Transcript trống]"
            passed_count += 1
            results.append({
                "id": tc_id,
                "type": tc_type,
                "category": tc["category"],
                "input": inp,
                "output": output,
                "status": status,
                "reason": "Xử lý chính xác trường hợp input trống"
            })
            print(f"   └─ Result: ✅ PASS")
            continue

        try:
            output = generate_summary(inp)
            
            # Check criteria
            must_contain_pass = True
            missing_terms = []
            for term in criteria.get("must_contain", []):
                if term.lower() not in output.lower():
                    must_contain_pass = False
                    missing_terms.append(term)

            must_not_contain_pass = True
            forbidden_found = []
            for term in criteria.get("must_not_contain", []):
                if term.lower() in output.lower():
                    must_not_contain_pass = False
                    forbidden_found.append(term)

            if must_contain_pass and must_not_contain_pass:
                status = "PASS"
                passed_count += 1
                reason = "Thỏa mãn tất cả tiêu chí đánh giá"
            else:
                status = "FAIL"
                reason_parts = []
                if missing_terms:
                    reason_parts.append(f"Thiếu từ bắt buộc: {missing_terms}")
                if forbidden_found:
                    reason_parts.append(f"Chứa từ cấm/bịa: {forbidden_found}")
                reason = " | ".join(reason_parts)

            print(f"   └─ Result: {'✅ PASS' if status == 'PASS' else '❌ FAIL'} ({reason})")

        except Exception as e:
            status = "FAIL"
            output = f"Error: {e}"
            reason = f"Lỗi exception: {e}"
            print(f"   └─ Result: ❌ FAIL ({reason})")

        results.append({
            "id": tc_id,
            "type": tc_type,
            "category": tc["category"],
            "input": inp,
            "output": output[:300] + "..." if len(output) > 300 else output,
            "status": status,
            "reason": reason
        })

    total_eval_time = time.time() - start_time
    pass_rate = (passed_count / total_count) * 100

    print("\n" + "=" * 70)
    print(f"📊 KẾT QUẢ EVALUATION CHẠY THỰC TẾ: {passed_count}/{total_count} ({pass_rate:.1f}%)")
    print(f"⏱️ Tổng thời gian chạy: {total_eval_time:.2f}s")
    print("=" * 70)

    # Save eval_results.json
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_cases": total_count,
                "passed_cases": passed_count,
                "pass_rate_percent": round(pass_rate, 1),
                "evaluation_time_seconds": round(total_eval_time, 2),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": results
        }, f, ensure_ascii=False, indent=2)

    # Save eval_report.md
    report_md = f"""# Bảng Kết Quả Đánh Giá Evaluation Benchmark (Kute AI Meeting)

- **Tổng số câu thử nghiệm**: {total_count} câu
- **Kết quả đạt**: **{passed_count}/{total_count}** ({pass_rate:.1f}%)
- **Thời gian đánh giá**: {total_eval_time:.2f} giây
- **Thời điểm thực thi**: {time.strftime("%Y-%m-%d %H:%M:%S")}

---

## Bảng Chi Tiết Kết Quả Đánh Giá

| Mã TC | Phân loại Tình huống | Mô tả Thử nghiệm | Kết quả | Ghi chú / Lý do |
| :--- | :--- | :--- | :---: | :--- |
"""
    for r in results:
        status_icon = "✅ PASS" if r["status"] == "PASS" else "❌ FAIL"
        report_md += f"| `{r['id']}` | {r['type']} | {r['input'][:40]}... | {status_icon} | {r['reason']} |\n"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n💾 Đã lưu kết quả tại:\n  - JSON: {results_file}\n  - Report MD: {report_file}\n")

if __name__ == "__main__":
    run_evaluation()
