"""
Parse batch collection log and create summary report
"""
import re
from datetime import datetime

def parse_batch_log(log_file_path, output_file_path):
    """Parse batch collection log and create summary"""

    # Try different encodings
    encodings = ['utf-8', 'cp949', 'euc-kr', 'utf-8-sig']
    log_content = None

    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding, errors='ignore') as f:
                log_content = f.read()
            break
        except:
            continue

    if log_content is None:
        print(f"Failed to read log file: {log_file_path}")
        return

    # Extract keyword results
    keyword_pattern = r"Processing keyword (\d+)/(\d+): '([^']+)' \(category: ([^\)]+)\)"
    result_pattern = r"수집 완료: (.+?) in (\w+)\s+- 총 수집 비디오 수: (\d+)개\s+- 필터링 후: (\d+)개\s+- Raw 데이터: (\d+)개\s+- 최종 반환: (\d+)개\s+- 총 API 호출 수: (\d+)"

    keywords_info = re.findall(keyword_pattern, log_content)
    results_info = re.findall(result_pattern, log_content)

    # Create summary report
    with open(output_file_path, 'w', encoding='utf-8') as out:
        out.write("="*80 + "\n")
        out.write("YouTube Batch Collection Summary Report\n")
        out.write("="*80 + "\n")
        out.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        total_api_calls = 0
        total_raw_videos = 0
        total_filtered_videos = 0
        total_keywords_processed = 0

        for i, result in enumerate(results_info):
            keyword_name, region, total_collected, filtered, raw, final, api_calls = result

            # Find corresponding keyword info
            keyword_idx = i + 1
            category = ""
            if i < len(keywords_info):
                category = keywords_info[i][3]

            total_api_calls += int(api_calls)
            total_raw_videos += int(raw)
            total_filtered_videos += int(filtered)
            total_keywords_processed += 1

            # Calculate API units (approximate)
            # search().list() = 100 units per call
            # videos().list() = 1 unit per call (up to 50 videos)
            # channels().list() = 1 unit per call
            # Assume: search + videos + channels for each batch of 50
            # Each batch: 100 (search) + 1 (videos) + 1 (channels) = 102 units
            num_batches = (int(total_collected) + 49) // 50
            estimated_units = num_batches * 102

            out.write(f"\n{'='*80}\n")
            out.write(f"Keyword {keyword_idx}: '{keyword_name}' (category: {category})\n")
            out.write(f"{'='*80}\n")
            out.write(f"  Region: {region}\n")
            out.write(f"  Total collected (unique): {total_collected}개\n")
            out.write(f"  Raw data saved: {raw}개\n")
            out.write(f"  Quality filter passed: {filtered}개\n")
            out.write(f"  Final returned: {final}개\n")
            out.write(f"  API calls: {api_calls}회\n")
            out.write(f"  Estimated API units used: ~{estimated_units} units\n")

            # Extract batch details if available
            keyword_section = log_content.split(f"Processing keyword {keyword_idx}/")[1].split("Processing keyword")[0] if keyword_idx < len(keywords_info) else log_content.split(f"Processing keyword {keyword_idx}/")[1]

            # Count batches
            batch_matches = re.findall(r'\[배치 (\d+)\].*?새로운 raw 비디오: (\d+)개', keyword_section, re.DOTALL)
            if batch_matches:
                out.write(f"\n  Batch details:\n")
                for batch_num, new_raw in batch_matches:
                    out.write(f"    - Batch {batch_num}: {new_raw}개 새로운 비디오\n")

        # Overall summary
        out.write(f"\n\n{'='*80}\n")
        out.write("Overall Summary\n")
        out.write(f"{'='*80}\n")
        out.write(f"Total keywords processed: {total_keywords_processed}\n")
        out.write(f"Total raw videos collected: {total_raw_videos}개\n")
        out.write(f"Total quality-filtered videos: {total_filtered_videos}개\n")
        out.write(f"Total API calls: {total_api_calls}회\n")

        # Estimate total API units
        total_batches = (total_raw_videos + 49) // 50
        estimated_total_units = total_batches * 102
        out.write(f"Estimated total API units: ~{estimated_total_units} units\n")
        out.write(f"API quota usage: ~{estimated_total_units / 10000 * 100:.1f}% of daily 10,000 units\n")

        out.write(f"\n{'='*80}\n")

    print(f"Summary report saved to: {output_file_path}")

if __name__ == "__main__":
    import sys

    log_file = sys.argv[1] if len(sys.argv) > 1 else "batch_collect_final_run.log"
    output_file = log_file.replace(".log", "_summary.txt")

    parse_batch_log(log_file, output_file)
