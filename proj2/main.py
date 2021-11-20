import os
import json
import sys
import albumentations

p21 = float(sys.argv[1]) if len(sys.argv) > 1 else None
p22 = float(sys.argv[2]) if len(sys.argv) > 2 else None
print("Project 2: taking params:", p21, p22)

obj = None
with open(
    "/home/termanteus/workspace/mlops/playground/pipeline/output/prj1.json", "r"
) as f:
    obj = json.load(f)
obj["p2"] = [p21, p22]

with open(
    "/home/termanteus/workspace/mlops/playground/pipeline/output/prj2.json", "w"
) as f:
    json.dump(obj, f)

print("Finish project 2")
