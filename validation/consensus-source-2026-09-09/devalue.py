# SvelteKit __data.json 의 devalue 평탄화 배열을 원래 중첩 구조로 복원한다.
import json


def unflatten(arr):
    if not isinstance(arr, list):
        return arr
    seen = {}

    def hydrate(idx):
        if idx == -1:
            return None
        if idx == -2:
            return None  # undefined
        if idx == -3:
            return float("nan")
        if idx == -4:
            return float("inf")
        if idx == -5:
            return float("-inf")
        if idx == -6:
            return -0.0
        if idx in seen:
            return seen[idx]
        v = arr[idx]
        if isinstance(v, list):
            out = []
            seen[idx] = out
            for e in v:
                out.append(hydrate(e))
            return out
        if isinstance(v, dict):
            out = {}
            seen[idx] = out
            for k, e in v.items():
                out[k] = hydrate(e)
            return out
        seen[idx] = v
        return v

    return hydrate(0)


def node_data(text, node_index):
    doc = json.loads(text)
    node = doc["nodes"][node_index]
    if node is None or node.get("type") != "data":
        return None
    return unflatten(node["data"])
