# 공개 HTTP GET 전용 헬퍼. import 시 부작용이 없어야 하므로 수집 로직과 분리한다.
import gzip
import time
import zlib
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url, timeout=30, hdrs=None, referer=None):
    h = {"User-Agent": UA,
         "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
         "Accept-Language": "en-US,en;q=0.9",
         "Accept-Encoding": "gzip, deflate"}
    if referer:
        h["Referer"] = referer
    if hdrs:
        h.update(hdrs)
    req = urllib.request.Request(url, headers=h)
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            enc = (r.headers.get("Content-Encoding") or "").lower()
            if enc == "gzip":
                raw = gzip.decompress(raw)
            elif enc == "deflate":
                raw = zlib.decompress(raw, -zlib.MAX_WBITS)
            return dict(ok=True, status=r.status, final_url=r.geturl(),
                        ctype=r.headers.get("Content-Type"), bytes=len(raw),
                        elapsed=round(time.time() - t0, 2),
                        text=raw.decode("utf-8", "replace"), error=None)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return dict(ok=False, status=e.code, final_url=url, ctype=None,
                    bytes=len(body), elapsed=round(time.time() - t0, 2),
                    text=body.decode("utf-8", "replace"), error="HTTPError %s" % e.code)
    except Exception as e:
        return dict(ok=False, status=None, final_url=url, ctype=None, bytes=0,
                    elapsed=round(time.time() - t0, 2), text="",
                    error="%s: %s" % (type(e).__name__, e))


def utcnow():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
