import re
import sys
from typing import Dict, List, Tuple

def extract_metrics(line: str) -> Dict[str, int]:
    """Extract metrics from a log line."""
    metrics_match = re.search(r'final_metrics=TrieNodeIterMetrics\s*\{\s*(.*?)\s*\}', line)
    if not metrics_match:
        return {}

    metrics_text = metrics_match.group(1)
    metrics = {}

    # Extract each metric using regex
    for pair in metrics_text.split(','):
        key_value = pair.strip().split(':')
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = int(key_value[1].strip())
            metrics[key] = value

    return metrics

def compare_logs(file1: str, file2: str) -> List[Tuple[int, int, float, float]]:
    """Compare hashed_cursor_seek_count between two log files."""
    results = []

    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        for i, (line1, line2) in enumerate(zip(f1, f2), 1):
            metrics1 = extract_metrics(line1)
            metrics2 = extract_metrics(line2)

            if not metrics1 or not metrics2:
                continue

            seek_count1 = metrics1.get('hashed_cursor_seek_count', 0)
            seek_count2 = metrics2.get('hashed_cursor_seek_count', 0)

            if seek_count1 > 0:
                improvement = (seek_count1 - seek_count2) / seek_count1 * 100
                multiplier = seek_count1 / seek_count2 if seek_count2 > 0 else float('inf')
            else:
                improvement = 0
                multiplier = 1.0

            results.append((seek_count1, seek_count2, improvement, multiplier))

    return results

def main():
    if len(sys.argv) != 3:
        print("Usage: python log_comparison.py file1.log file2.log")
        sys.exit(1)

    file1 = sys.argv[1]
    file2 = sys.argv[2]

    results = compare_logs(file1, file2)

    # Print summary
    print(f"{'Line':^10} | {'Original':^15} | {'New':^15} | {'Improvement':^15} | {'Multiplier':^15}")
    print("-" * 80)

    total_original = 0
    total_new = 0

    for i, (original, new, improvement, multiplier) in enumerate(results, 1):
        multiplier_str = f"{multiplier:.2f}x" if multiplier != float('inf') else "∞"
        print(f"{i:^10} | {original:^15} | {new:^15} | {improvement:^.2f}% | {multiplier_str:^15}")
        total_original += original
        total_new += new

    # Calculate overall improvement
    if total_original > 0:
        overall_improvement = (total_original - total_new) / total_original * 100
        overall_multiplier = total_original / total_new if total_new > 0 else float('inf')
    else:
        overall_improvement = 0
        overall_multiplier = 1.0

    print("-" * 80)
    overall_multiplier_str = f"{overall_multiplier:.2f}x" if overall_multiplier != float('inf') else "∞"
    print(f"{'Total':^10} | {total_original:^15} | {total_new:^15} | {overall_improvement:^.2f}% | {overall_multiplier_str:^15}")

if __name__ == "__main__":
    main()
