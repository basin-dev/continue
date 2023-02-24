from typing import Dict, List
from .models import RangeInFile, Range

def merge_ranges_in_files(ranges_in_files: List[RangeInFile]) -> List[RangeInFile]:
    """Merge overlapping ranges in the same file."""
    file_buckets: Dict[str, List[RangeInFile]] = {}
    for r in ranges_in_files:
        if r.filepath not in file_buckets:
            file_buckets[r.filepath] = []
        file_buckets[r.filepath].append(r)

    merged = []
    for filepath, ranges in file_buckets.items():
        ranges.sort(key=lambda r: r.range.start)
        merged_ranges = [ranges[0]]
        for r in ranges[1:]:
            if r.range.start <= merged_ranges[-1].range.end:
                merged_ranges[-1].range = r.range.union(merged_ranges[-1].range)
            else:
                merged_ranges.append(r)

        merged.extend(merged_ranges)
    
    return merged
    