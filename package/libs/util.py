from typing import Dict, List
from .models.main import RangeInFile, Traceback
from boltons import tbutils

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
    
def parse_traceback(stderr: str) -> Traceback:
    # Sometimes paths are not quoted, but they need to be
    if "File \"" not in stderr:
        stderr = stderr.replace("File ", "File \"").replace(", line ", "\", line ")
    tbutil_parsed_exc = tbutils.ParsedException.from_string(stderr)
    return Traceback.from_tbutil_parsed_exc(tbutil_parsed_exc)