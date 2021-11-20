import numpy
import os
import json
import sys

p11 = float(sys.argv[1]) if len(sys.argv) > 1 else None
p12 = float(sys.argv[2]) if len(sys.argv) > 2 else None
p13 = float(sys.argv[3]) if len(sys.argv) > 2 else None
print("Project 1: taking params:", p11, p12, p13)

with open(
    "/home/termanteus/workspace/mlops/playground/pipeline/output/prj1.json", "w"
) as f:
    json.dump({"p1": [p11, p12, p13]}, f)

print("Finish project 1")
