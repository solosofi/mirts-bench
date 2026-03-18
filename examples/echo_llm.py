import json
import sys

_ = sys.stdin.read()
print(json.dumps({"type": "end_turn"}))
