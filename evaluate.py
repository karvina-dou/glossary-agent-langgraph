import sys
import glob
import json
from pathlib import Path


if __name__ == '__main__':
    result_dir = sys.argv[1:][0]
    total_fp = 0
    for result_js in sorted(glob.glob(f'{result_dir}/*.json')):
        result = json.load(open(result_js, 'r'))

        # count False Positive
        fp = sum([1 for k, v in result.items() if not eval(v['response'])])
        print(Path(result_js).stem, fp)
        total_fp += fp
    print(total_fp)
