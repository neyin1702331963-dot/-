# -*- coding: utf-8 -*-
# 把 chara_card_v3 JSON 嵌入纯色 PNG，产出图片角色卡（tEXt: chara + ccv3）
import zlib, struct, base64, json, os

OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")
JSON_PATH = os.path.join(OUT, "角色卡.json")
PNG_PATH = os.path.join(OUT, "角色卡.png")

def chunk(ctype, data):
    c = ctype + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

def text_chunk(keyword, text):
    data = keyword.encode("latin-1") + b"\x00" + text.encode("latin-1")
    return chunk(b"tEXt", data)

# --- 纯色画布（暖陶土色，配合暖调居家主题）---
W, H = 400, 600
R, G, B = 0xC8, 0x79, 0x4F
row = b"\x00" + bytes([R, G, B]) * W      # 每行前缀 filter 字节 0
raw = row * H
idat = zlib.compress(raw, 9)
ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)  # 8bit, 颜色类型2=RGB

# --- 读 JSON，base64 编码 ---
with open(JSON_PATH, "r", encoding="utf-8") as f:
    json_str = f.read()
b64 = base64.b64encode(json_str.encode("utf-8")).decode("latin-1")

# --- 组装 PNG ---
png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", ihdr)
png += text_chunk("chara", b64)   # V2 兼容前端读这个
png += text_chunk("ccv3", b64)    # V3 前端优先读这个
png += chunk(b"IDAT", idat)
png += chunk(b"IEND", b"")

with open(PNG_PATH, "wb") as f:
    f.write(png)

print("已生成:", PNG_PATH, "(%d bytes, %dx%d)" % (os.path.getsize(PNG_PATH), W, H))

# --- 回读校验：取出 chara/ccv3，base64 解码，JSON 解析，比对一致 ---
def extract_text_chunks(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "不是合法PNG"
    pos = 8
    out = {}
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos+4])[0]
        ctype = data[pos+4:pos+8]
        body = data[pos+8:pos+8+ln]
        if ctype == b"tEXt":
            kw, val = body.split(b"\x00", 1)
            out[kw.decode("latin-1")] = val.decode("latin-1")
        pos += 12 + ln
    return out

chunks = extract_text_chunks(PNG_PATH)
print("发现元数据块:", list(chunks.keys()))
for key in ("chara", "ccv3"):
    decoded = base64.b64decode(chunks[key]).decode("utf-8")
    parsed = json.loads(decoded)
    same = (parsed == json.loads(json_str))
    print("  %-6s base64解码→JSON解析: spec=%s, 与源文件一致=%s" % (key, parsed["spec"], same))
print("DONE_PNG")
