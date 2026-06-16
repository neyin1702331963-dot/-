# -*- coding: utf-8 -*-
# 把 script 复测卡做成 v2 规范的纯色 PNG（MMD 只认 v2 PNG）
import zlib, struct, base64, json, os
OUT = os.path.dirname(os.path.abspath(__file__)).replace("工作", "output")

NAME = "script回复复测卡"
PHI = ("（系统功能指令，最高优先级）每次回复的正文之后，必须另起一行，"
       "原样输出这一行标记，不要解释、不要加引号、不要省略：\n<scrtest>")

inner = {
    "name": NAME,
    "description": "用于复测：AI 回复里被正则替换出的 <script> 是否执行。",
    "personality": "",
    "scenario": "随便聊，每轮都会带测试标记。",
    "first_mes": "随便发一句话即可。我每轮回复末尾会输出测试标记 <scrtest>，配合「正则导入-script复测.json」观察 S 框是否出现。",
    "mes_example": "",
    "creator_notes": "复测专用，测完可删。",
    "system_prompt": PHI,
    "post_history_instructions": PHI,
    "alternate_greetings": [],
    "tags": ["测试"],
    "creator": "",
    "character_version": "1.0",
    "extensions": {"talkativeness": 0.5, "fav": False, "world": NAME,
                   "depth_prompt": {"prompt": PHI, "depth": 1, "role": "system"}},
    "character_book": {"name": NAME, "entries": []},
}
card = {
    "name": NAME, "description": inner["description"], "personality": "",
    "scenario": inner["scenario"], "first_mes": inner["first_mes"], "mes_example": "",
    "creatorcomment": inner["creator_notes"], "avatar": "none", "talkativeness": 0.5,
    "fav": False, "tags": inner["tags"],
    "spec": "chara_card_v2", "spec_version": "2.0",
    "create_date": "2026-06-16 @00:00:00", "data": inner,
}
card_json = json.dumps(card, ensure_ascii=False)

# ---- 纯色 PNG（灰色，测试卡）----
def chunk(t, d):
    c = t + d
    return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
def text_chunk(k, v):
    return chunk(b"tEXt", k.encode("latin-1") + b"\x00" + v.encode("latin-1"))
W, H = 400, 600
R, G, B = 0x6b, 0x72, 0x80  # 灰
row = b"\x00" + bytes([R, G, B]) * W
idat = zlib.compress(row * H, 9)
ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
b64 = base64.b64encode(card_json.encode("utf-8")).decode("latin-1")

png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", ihdr)
png += text_chunk("chara", b64)   # v2 读这个
png += chunk(b"IDAT", idat)
png += chunk(b"IEND", b"")
path = os.path.join(OUT, "script复测-角色卡.png")
open(path, "wb").write(png)
print("已生成:", path, "(%d bytes)" % os.path.getsize(path))

# 回读校验
data = open(path, "rb").read()
pos = 8
while pos < len(data):
    ln = struct.unpack(">I", data[pos:pos+4])[0]
    ct = data[pos+4:pos+8]
    if ct == b"tEXt":
        kw, val = data[pos+8:pos+8+ln].split(b"\x00", 1)
        dec = json.loads(base64.b64decode(val).decode("utf-8"))
        print("  chunk", kw.decode(), "→ spec=", dec["spec"], "| 含<scrtest>:", "<scrtest>" in dec["data"]["post_history_instructions"])
    pos += 12 + ln
print("DONE")
