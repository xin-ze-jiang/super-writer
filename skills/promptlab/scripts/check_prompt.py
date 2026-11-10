#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PromptLab 提示词自检器（Python 3，无第三方依赖）

用法：
  python check_prompt.py -p "提示词"
  python check_prompt.py -f prompt.txt
  python check_prompt.py -b prompts.txt        # 每行一条，批量
  type prompt.txt | python check_prompt.py     # 或用管道
  python check_prompt.py --lang en -p "..."    # 强制英文模式（zh/en/auto，默认 auto）
退出码：0 全部可提交；1 有需修改项；2 用法或读取错误
"""

import argparse
import re
import sys
from collections import Counter

# ---------------------------------------------------------------- 基础统计
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
WORD_RE = re.compile(r"[A-Za-z]+|\d+(?:\.\d+)?")


def src_len(text: str) -> int:
    """按中文习惯计字数：汉字 1 字，英文/数字各算 1 个词。"""
    return len(CJK_RE.findall(text)) + len(WORD_RE.findall(text))


def count_words_en(text: str) -> int:
    """英文按词计数：空格分隔的字母数字串算 1 词，纯数字（如 16:9 里的 16）不算。"""
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text)
    return sum(1 for t in tokens if re.search(r"[A-Za-z]", t))


def detect_lang(text: str) -> str:
    """自动判定中/英：中文按汉字数，英文按字母词数；判不准时按占比。"""
    cjk = len(CJK_RE.findall(text))
    words = count_words_en(text)
    if cjk >= 12:
        return "zh"
    if words >= 12 and cjk <= 3:
        return "en"
    return "zh" if cjk >= words else "en"


def read_text_file(path: str) -> str:
    with open(path, "rb") as f:
        raw = f.read()
    for enc in ("utf-8-sig", "gbk", "utf-16"):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise SystemExit("[错误] 无法识别文件编码：%s（请存为 UTF-8）" % path)


# ---------------------------------------------------------------- 否定词
NEG_TERMS = ("不要", "不用", "没有", "避免", "勿", "禁止")
# 这些词组里的“否定字”是正常中文，不算否定句
NEG_WHITELIST = ("不要紧", "要不要", "要不是", "不得了",
                 "没有问题", "没什么", "没关系", "没有关系")


def _whitelist_spans(text):
    spans = []
    for w in NEG_WHITELIST:
        start = 0
        while True:
            i = text.find(w, start)
            if i < 0:
                break
            spans.append((i, i + len(w)))
            start = i + 1
    return spans


def check_negatives(text):
    spans = _whitelist_spans(text)
    hits, skipped = [], []
    for term in NEG_TERMS:
        start = 0
        while True:
            i = text.find(term, start)
            if i < 0:
                break
            if any(a <= i < b for a, b in spans):
                skipped.append(term)
            else:
                frag = text[max(0, i - 6): i + len(term) + 6]
                hits.append((i + 1, term, frag))
            start = i + len(term)
    return hits, skipped


# ---------------------------------------------------------------- 无效画质词
QUALITY_WORDS = (
    "8k", "4k", "超高清", "超清", "高清", "超精细", "极致", "杰作",
    "大师作品", "大师级", "顶级画质", "最佳画质", "电影级画质",
    "获奖作品", "获奖摄影", "完美画质", "render quality",
)
QUALITY_ADVICE = "画面分辨率由工具决定，这类词不改变画面，只占字数；改用“主体锐利，细节集中在材质表面，背景虚化”。"
# 最长优先匹配：避免“超高清”同时再算一次“高清”
QUALITY_RE = re.compile(
    "|".join(sorted((re.escape(w) for w in QUALITY_WORDS), key=len, reverse=True)),
    re.I,
)


def check_quality(text):
    return [(m.start() + 1, m.group()) for m in QUALITY_RE.finditer(text)]


# ---------------------------------------------------------------- 主体第一句
STYLE_LEAD = ("风格", "画风", "镜头", "光线", "画幅", "比例", "构图", "背景",
              "远景", "中景", "近景", "特写", "画面", "整体", "超高清",
              "8k", "杰作", "大师", "唯美", "高级感", "氛围感")

SUBJECT_WORDS = (
    "人", "女", "男", "女孩", "男孩", "女生", "男生", "少女", "少年", "孩子",
    "儿童", "老人", "女人", "男人", "母亲", "父亲", "猫", "狗", "鸟", "兔",
    "熊", "龙", "马", "牛", "羊", "象", "鱼", "机器人", "怪物", "精灵",
    "骑士", "士兵", "宇航员", "机械", "动物", "角色", "主角", "主体",
    "船", "车", "房子", "建筑", "城市", "森林", "山", "海", "街道", "巷",
    "房间", "教室", "厨房", "卧室", "仓库", "厂房", "展厅", "空间", "室内",
    "室外", "码头", "港口", "广场", "舞台", "营地", "洞穴", "神殿",
    "实验室", "工厂", "桌", "椅", "树", "花", "产品", "模型",
)

ACTION_WORDS = (
    "站", "坐", "蹲", "跪", "跑", "奔", "走", "骑", "飞", "飘", "看", "望",
    "抬头", "低头", "回望", "注视", "凝视", "拿", "抱", "举", "捧", "推",
    "拉", "躺", "倚", "靠", "穿", "翻", "读", "伸", "挥", "背", "扛",
    "俯身", "微笑", "笑", "哭", "转身", "跃", "跳", "漂浮", "悬停",
    "张开", "握住", "打开", "合上", "搬", "运", "停靠", "改造", "堆叠",
    "趴", "卧", "吃", "喝", "唱", "演奏", "写字", "作画", "落下", "飞过",
    "改为", "换成", "替换", "添加", "删除", "调整", "变成", "保持",
)


CLAUSE_SPLIT = re.compile(r"[，,、；;。！？!?\n]")


def split_first_sentence(text):
    """返回首句（第一分句；太短时顺延合并下一分句）。"""
    body = text.strip().lstrip("，,、；;：:。 ")
    parts = [p.strip() for p in CLAUSE_SPLIT.split(body) if p.strip()]
    if not parts:
        return ""
    first = parts[0]
    for nxt in parts[1:3]:
        if len(CJK_RE.findall(first)) >= 8:
            break
        first += "，" + nxt
    return first


EDIT_RE = re.compile(r"生成[：:]?")


def is_edit_mode(text):
    return "参考图" in text and EDIT_RE.search(text) is not None


def check_subject(text):
    mode = "普通"
    body = text
    m = EDIT_RE.search(text)
    if "参考图" in text and m:        # 参考图编辑模式：主体判断看“生成：”之后的段落
        body = text[m.end():]
        mode = "参考图编辑"
    first = split_first_sentence(body)
    notes = []
    fail = False

    low_head = first[:6].lower()
    if any(low_head.startswith(w) for w in STYLE_LEAD):
        fail = True
        notes.append("第一句以风格/镜头/画幅类词开头，主体被压后")

    has_subject = any(w in first for w in SUBJECT_WORDS)
    has_action = any(w in first for w in ACTION_WORDS)

    if not has_subject:
        fail = True
        notes.append("第一句没找到明确主体（谁/什么）")
    if not has_action:
        notes.append("第一句缺动作，补“正在做什么”")

    ok = (not fail) and has_action
    return {
        "ok": ok,
        "fail": fail,
        "mode": mode,
        "first": first,
        "notes": notes,
        "deduct": (15 if fail else (8 if not has_action else 0)),
    }


# ---------------------------------------------------------------- 三要素
FIG_RE = re.compile(r"\d{1,2}\s*:\s*\d{1,2}")
FIG_WORDS = ("画幅", "比例", "竖版", "横版", "方图", "宽幅", "宽银幕")
LENS_WORDS = ("镜头", "mm", "焦段", "机位", "景深", "虚化", "光斑", "广角",
              "超广角", "长焦", "微距", "鱼眼", "俯拍", "仰拍", "平视",
              "齐眼", "追随", "定格", "等轴测", "平行投影", "标准镜头")
LIGHT_WORDS = ("光", "阴影", "逆光", "侧光", "顺光", "顶光", "底光", "柔光",
               "硬光", "补光", "轮廓光", "体积光", "霓虹", "烛光", "聚光",
               "反光", "黄金时刻", "蓝调", "清晨", "黄昏", "阴天", "夜晚",
               "正午", "日出", "照明", "光束")


def _scrub_negated(text):
    """去掉“不要看镜头/没有阳光”这类被否定掉的内容，避免误判为已具备。"""
    spans = _whitelist_spans(text)
    out, last = [], 0
    for m in re.finditer(r"(?:不要|不用|没有|避免|勿|禁止)[^，。；;\n]{0,10}", text):
        if any(a <= m.start() < b for a, b in spans):
            continue
        out.append(text[last:m.start()])
        last = m.end()
    out.append(text[last:])
    return "".join(out)


def check_elements(text, edit=False):
    body = _scrub_negated(text)
    low = body.lower()
    fig = any(w in body for w in FIG_WORDS) or bool(FIG_RE.search(body))
    lens = any(w in low for w in LENS_WORDS)
    light = any(w in body for w in LIGHT_WORDS)
    missing = []
    if not fig:
        missing.append("画幅（如“画幅 3:4”）")
    if not lens:
        missing.append("镜头（焦段/机位/景深，如“85mm，胸口机位，浅景深”）")
    if not light:
        missing.append("光线（方向+时间，如“主光来自画面左上，阴天散射光”）")
    if edit:                     # 编辑模式：三要素沿用参考图，不必重复写
        return {"fig": fig, "lens": lens, "light": light,
                "missing": [], "edit": True, "deduct": 0}
    return {"fig": fig, "lens": lens, "light": light,
            "missing": missing, "edit": False, "deduct": 8 * len(missing)}


# ---------------------------------------------------------------- 冲突/堆叠
CONFLICT_GROUPS = (
    ("广角与长焦互斥", ("广角", "长焦")),                # 超广角也算广角，另判
    ("同类焦段堆叠", ("广角", "超广角", "鱼眼")),
    ("景别自相矛盾", ("远景", "特写")),
    ("景别重复", ("中景", "近景")),
    ("绘画媒介互斥", ("水彩", "油画", "水墨", "版画")),
    ("画风互斥", ("绘本", "动漫", "二次元")),
    ("饱和度互斥", ("高饱和", "低饱和")),
    ("光位互斥", ("逆光", "顺光")),
    ("清晰度互斥", ("浅景深", "全画面清晰")),
    ("色温互斥", ("暖色调", "冷色调")),
    ("构图规则互斥", ("三分法", "中心对称")),
    ("渲染与摄影互斥", ("三维渲染", "摄影")),
)


def _matched_terms(text, terms):
    """最长优先匹配，避免“超广角”被当成“广角”再算一次。"""
    pattern = re.compile("|".join(sorted((re.escape(t) for t in terms),
                                         key=len, reverse=True)))
    return {m.group() for m in pattern.finditer(text)}


def check_conflicts(text):
    issues = []
    for name, terms in CONFLICT_GROUPS:
        found = _matched_terms(text, terms)
        if len(found) >= 2:
            issues.append("%s：%s" % (name, " / ".join(sorted(found, key=len, reverse=True))))
    return issues


REPEAT_WHITELIST = ("保持不变", "保持一致", "参考图", "同一角色", "画面中")


def check_repeats(text):
    """查同一段汉字里重复出现的 4~8 字短语。"""
    dup = Counter()
    for run in re.findall(r"[\u4e00-\u9fff]{4,}", text):
        for n in range(4, min(8, len(run)) + 1):
            for i in range(len(run) - n + 1):
                dup[run[i:i + n]] += 1
    reps = [(p, c) for p, c in dup.items() if c >= 2]
    reps.sort(key=lambda x: (-len(x[0]), x[0]))
    kept = []
    for phrase, cnt in reps:
        if any(phrase in longer and cnt <= lcnt for longer, lcnt in kept):
            continue
        if any(w in phrase for w in REPEAT_WHITELIST):
            continue
        kept.append((phrase, cnt))
    return ["“%s”出现 %d 次" % (p, c) for p, c in kept[:4]]


# ---------------------------------------------------------------- 字数
def check_length(text, edit=False):
    n = src_len(text)
    if edit:                     # 编辑模式只写增量，允许更短
        if n > 120:
            seg, cut = _top_segments(text, 1)
            return {"n": n, "ok": False, "deduct": 10,
                    "msg": "编辑模式超长（%d 字，上限 120）：增量只写改动处，建议删 %s" % (n, seg)}
        return {"n": n, "ok": True, "deduct": 0,
                "msg": "编辑模式（只写增量，%d 字，允许 25~120）" % n}
    if n < 60:
        return {"n": n, "ok": False, "deduct": 10,
                "msg": "偏短（%d 字）：补主体动作、镜头、光线、画幅，凑到 60 字以上" % n}
    if n > 200:
        seg, cut = _top_segments(text, 3)
        return {"n": n, "ok": False, "deduct": 15,
                "msg": "严重超长（%d 字）：删最长 3 段后约 %d 字 —— %s；仍超就只留“主体动作 + 一个环境 + 一处光 + 一个镜头 + 画幅”，其余拆成多条单独生成"
                       % (n, n - cut, seg)}
    if n > 120:
        seg, cut = _top_segments(text, 1)
        return {"n": n, "ok": False, "deduct": 10,
                "msg": "超长（%d 字，目标 60~120）：建议删 %s，删后约 %d 字"
                       % (n, seg, n - cut)}
    return {"n": n, "ok": True, "deduct": 0, "msg": "长度合格（%d 字）" % n}


def _top_segments(text, top, unit="字"):
    """返回最长的 top 段（按原文顺序展示）与它们合计字数。"""
    parts = [p.strip() for p in re.split(r"[；;。\n]", text) if p.strip()]
    if len(parts) <= 1:                      # 一句话写到底时按逗号切
        parts = [p.strip() for p in re.split(r"[，,]", text) if p.strip()]
    if not parts:
        return "（无有效分段）", 0
    order = sorted(range(len(parts)), key=lambda i: src_len(parts[i]), reverse=True)[:top]
    order.sort()
    pieces, total = [], 0
    for i in order:
        piece = parts[i]
        total += src_len(piece)
        shown = piece if len(piece) <= 16 else piece[:16] + "…"
        pieces.append("第 %d 段「%s」（%d %s）" % (i + 1, shown, src_len(piece), unit))
    return "；".join(pieces), total


# ---------------------------------------------------------------- 英文模式
EN_STYLE_LEAD = (
    "8k", "4k", "masterpiece", "best quality", "highest quality", "ultra detailed",
    "highly detailed", "hyperrealistic", "photorealistic", "award", "cinematic",
    "cinematically", "high quality", "wide angle", "close up", "close-up",
    "aspect ratio", "shot on", "style", "lighting", "composition", "background",
)

EN_SUBJECT_WORDS = (
    "woman", "women", "man", "men", "girl", "boy", "child", "children",
    "kid", "baby", "babies", "person", "people", "lady", "gentleman",
    "cat", "dog", "bird", "rabbit", "bear", "dragon", "horse",
    "robot", "monster", "elf", "knight", "soldier", "astronaut", "character",
    "animal", "crowd", "ship", "boat", "car", "house", "building", "city",
    "forest", "mountain", "sea", "ocean", "street", "alley", "room",
    "classroom", "kitchen", "workshop", "factory", "warehouse", "stage",
    "cave", "temple", "laboratory", "table", "chair", "tree", "flower",
    "product", "model",
)

EN_ACTION_RE = re.compile(
    r"\b(?:stand(?:s|ing)?|sit(?:s|ting)?|walk(?:s|ing)?|run(?:s|ning)?|"
    r"kneel(?:s|ing)?|crouch(?:es|ing)?|hold(?:s|ing)?|look(?:s|ing)?|"
    r"gaz(?:e|es|ing)|reach(?:es|ing)?|lift(?:s|ing)?|carr(?:y|ies|ying)|"
    r"read(?:s|ing)?|open(?:s|ing)?|clos(?:e|es|ing|ed)|paint(?:s|ing)?|"
    r"play(?:s|ing)?|float(?:s|ing)?|fl(?:y|ies|ying)|lean(?:s|ing)?|"
    r"li(?:e|es|ing)|sleep(?:s|ing)?|eat(?:s|ing)?|drink(?:s|ing)?|"
    r"turn(?:s|ing)?|smil(?:e|es|ing)|wait(?:s|ing)?|work(?:s|ing)?|"
    r"build(?:s|ing)?|repair(?:s|ing)?|push(?:es|ing)?|pull(?:s|ing)?|"
    r"climb(?:s|ing)?|jump(?:s|ing)?|danc(?:e|es|ing)|sing(?:s|ing)?|"
    r"brush(?:es|ing)?|pour(?:s|ing)?|cut(?:s|ting)?)\b",
    re.I,
)

EN_NEG_RE = re.compile(
    r"\b(?:no|not|never|without|avoid\w*|don['’]t|do not|cannot|can['’]t|none)\b",
    re.I,
)

EN_QUALITY_TERMS = (
    "8k", "4k", "ultra detailed", "ultra-detailed", "hyper detailed", "hyper-detailed",
    "highly detailed", "masterpiece", "best quality", "highest quality",
    "hyperrealistic", "hyper realistic", "award winning", "award-winning",
    "photorealistic", "ultra high definition", "8k resolution", "4k resolution",
)

EN_FIG_RE = re.compile(r"\b\d{1,2}\s*:\s*\d{1,2}\b")
EN_FIG_WORDS = ("aspect ratio", "vertical format", "vertical composition",
                "horizontal format", "landscape format", "portrait format",
                "square format", "widescreen", "full frame", "cinemascope")
EN_LENS_WORDS = (
    "lens", "focal", "close up", "wide shot", "medium shot", "full shot",
    "long shot", "extreme wide", "establishing shot", "over the shoulder",
    "pov", "depth of field", "bokeh", "aperture", "camera angle", "low angle",
    "high angle", "eye level", "telephoto", "wide angle", "macro lens", "zoom",
    "dolly", "handheld", "steadicam", "tripod", "prime lens", "shot size",
)
EN_LIGHT_WORDS = (
    "light", "lights", "lighting", "lit", "sunlight", "sunlit", "backlight",
    "backlit", "rim light", "key light", "fill light", "spotlight", "shadow",
    "golden hour", "blue hour", "overcast", "diffused", "neon", "candlelight",
    "candlelit", "volumetric", "soft light", "hard light", "daylight", "dusk",
    "dawn", "night", "moonlit", "sunrise", "sunset", "glow",
)
EN_MM_RE = re.compile(r"\b\d{2,3}\s*mm\b", re.I)

EN_CONFLICT_GROUPS = (
    ("广角与长焦互斥", ("wide angle", "telephoto")),
    ("景别自相矛盾", ("wide shot", "close up")),
    ("绘画媒介互斥", ("watercolor", "oil painting")),
    ("饱和度互斥", ("high saturation", "low saturation")),
    ("光位互斥", ("backlight", "front light")),
    ("清晰度互斥", ("shallow depth of field", "deep focus")),
    ("色温互斥", ("warm tones", "cool tones")),
)

EN_QUALITY_ADVICE = "分辨率与精细度由工具决定，这类词不改变画面，只占词数；改用具体材质、光源与镜头描述。"


def _norm_en(text):
    low = text.lower().replace("’", "'")
    low = re.sub(r"[-_]", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def _term_re(terms):
    """把词表编成"按词边界匹配"的正则，避免 light 命中 delight、mm 命中 immersive。"""
    parts = []
    for t in sorted(terms, key=len, reverse=True):
        words = [w for w in re.split(r"[\s\-]+", t) if w]
        parts.append(r"[\s\-]+".join(re.escape(w) for w in words))
    return re.compile(r"(?<!\w)(?:%s)(?!\w)" % "|".join(parts), re.I)


EN_FIG_TERM_RE = _term_re(EN_FIG_WORDS)
EN_LENS_TERM_RE = _term_re(EN_LENS_WORDS)
EN_LIGHT_TERM_RE = _term_re(EN_LIGHT_WORDS)


def split_first_sentence_en(text):
    body = text.strip().lstrip(".,;:!? ")
    parts = [p.strip() for p in re.split(r"[.,;:!?\n]", body) if p.strip()]
    if not parts:
        return ""
    first = parts[0]
    for nxt in parts[1:4]:
        if count_words_en(first) >= 6:
            break
        first += ", " + nxt
    return first


def check_negatives_en(text):
    hits = []
    for m in EN_NEG_RE.finditer(text):
        frag = text[max(0, m.start() - 12): m.end() + 12].replace("\n", " ")
        hits.append((m.start() + 1, m.group(), frag))
    return hits


def check_quality_en(text):
    norm = _norm_en(text)
    found, seen = [], set()
    for w in sorted(EN_QUALITY_TERMS, key=len, reverse=True):
        key = _norm_en(w)
        if key in seen or key not in norm:
            continue
        seen.add(key)
        found.append(w)
    return [(0, w) for w in found]


def check_subject_en(text):
    first = split_first_sentence_en(text)
    notes = []
    fail = False
    head = _norm_en(first)
    if any(head.startswith(w) for w in EN_STYLE_LEAD):
        fail = True
        notes.append("第一句以风格/镜头/技术词开头，主体被压后")
    subj_re = re.compile(
        r"\b(?:%s)(?:s|es|'s)?\b" % "|".join(
            re.escape(w) for w in sorted(EN_SUBJECT_WORDS, key=len, reverse=True)),
        re.I,
    )
    has_subject = bool(subj_re.search(first))
    has_action = bool(EN_ACTION_RE.search(first))
    if not has_subject:
        fail = True
        notes.append("第一句没找到明确主体（谁/什么）")
    if not has_action:
        notes.append("第一句缺动作，补“正在做什么”")
    return {
        "ok": (not fail) and has_action,
        "fail": fail,
        "mode": "普通",
        "first": first,
        "notes": notes,
        "deduct": (15 if fail else (8 if not has_action else 0)),
    }


def _scrub_negated_en(text):
    return re.sub(r"\b(?:without|no|not|never|avoid\w*)\b[^.,;!?\n]{0,14}",
                  " ", text, flags=re.I)


def check_elements_en(text):
    body = _scrub_negated_en(text)
    fig = bool(EN_FIG_RE.search(body)) or bool(EN_FIG_TERM_RE.search(body))
    lens = bool(EN_LENS_TERM_RE.search(body)) or bool(EN_MM_RE.search(body))
    light = bool(EN_LIGHT_TERM_RE.search(body))
    missing = []
    if not fig:
        missing.append("画幅（如 “aspect ratio 16:9”）")
    if not lens:
        missing.append("镜头（焦段/景别，如 “35mm lens, medium shot”）")
    if not light:
        missing.append("光线（如 “soft window light from the upper left”）")
    return {"fig": fig, "lens": lens, "light": light,
            "missing": missing, "edit": False, "deduct": 8 * len(missing)}


def check_conflicts_en(text):
    norm = _norm_en(text)
    issues = []
    for name, terms in EN_CONFLICT_GROUPS:
        found = [t for t in terms if t in norm]
        if len(found) >= 2:
            issues.append("%s：%s" % (name, " / ".join(found)))
    return issues


def check_length_en(text):
    n = count_words_en(text)
    if n < 40:
        return {"n": n, "ok": False, "deduct": 10,
                "msg": "偏短（%d 词，目标 40~80）：补主体动作、镜头类型、光线、画幅" % n}
    if n > 100:
        seg, cut = _top_segments(text, 3, unit="词")
        return {"n": n, "ok": False, "deduct": 15,
                "msg": "严重超长（%d 词，目标 40~80）：删最长 3 段后约 %d 词 —— %s；仍超就只留“主体动作 + 一个环境 + 一处光 + 一个镜头 + 画幅”，其余拆成多条"
                       % (n, n - cut, seg)}
    if n > 80:
        seg, cut = _top_segments(text, 1, unit="词")
        return {"n": n, "ok": False, "deduct": 10,
                "msg": "超长（%d 词，目标 40~80）：建议删 %s，删后约 %d 词"
                       % (n, seg, n - cut)}
    return {"n": n, "ok": True, "deduct": 0, "msg": "长度合格（%d 词）" % n}


def inspect_en(text):
    neg_hits = check_negatives_en(text)
    quality = check_quality_en(text)
    subject = check_subject_en(text)
    elements = check_elements_en(text)
    conflicts = check_conflicts_en(text)
    length = check_length_en(text)

    must = []
    if length["deduct"]:
        must.append(length["msg"])
    if neg_hits:
        pos = "；".join("第 %d 字符「%s」" % (i, frag) for i, _t, frag in neg_hits[:3])
        must.append("否定句 %d 处（%s）：改成正向描述" % (len(neg_hits), pos))
    if quality:
        pos = "、".join("「%s」" % w for _i, w in quality[:6])
        must.append("无效画质词 %d 处（%s）：%s" % (len(quality), pos, EN_QUALITY_ADVICE))
    if subject["fail"]:
        must.append("主体位置不合格：%s" % "；".join(subject["notes"]))
    if elements["missing"]:
        must.append("缺三要素：%s" % "、".join(elements["missing"]))
    if conflicts:
        must.append("互斥/堆叠词：%s" % "；".join(conflicts))

    score = 100
    score -= min(24, 8 * len(neg_hits))
    score -= min(15, 5 * len(quality))
    score -= length["deduct"]
    score -= subject["deduct"]
    score -= elements["deduct"]
    score -= min(18, 6 * len(conflicts))
    score = max(0, score)

    return {
        "lang": "en",
        "len": length["n"],
        "length": length,
        "neg": neg_hits,
        "neg_skipped": [],
        "quality": quality,
        "subject": subject,
        "elements": elements,
        "conflicts": conflicts,
        "repeats": [],
        "must": must,
        "score": score,
        "verdict": "可提交" if score >= 85 and not must else "需修改",
    }


# ---------------------------------------------------------------- 汇总
def inspect(text, lang="auto"):
    text = text.strip()
    if lang in (None, "auto"):
        lang = detect_lang(text)
    if lang == "en":
        return inspect_en(text)
    edit = is_edit_mode(text)
    neg_hits, neg_skipped = check_negatives(text)
    quality = check_quality(text)
    subject = check_subject(text)
    elements = check_elements(text, edit)
    conflicts = check_conflicts(text)
    repeats = check_repeats(text)
    length = check_length(text, edit)

    must = []
    if length["deduct"]:
        must.append(length["msg"])
    if neg_hits:
        pos = "；".join("第 %d 字「%s」" % (i, frag) for i, _t, frag in neg_hits[:3])
        must.append("否定句 %d 处（%s）：改成正向描述" % (len(neg_hits), pos))
    if quality:
        pos = "、".join("「%s」" % w for _i, w in quality[:6])
        must.append("无效画质词 %d 处（%s）：%s" % (len(quality), pos, QUALITY_ADVICE))
    if subject["fail"]:
        must.append("主体位置不合格：%s" % "；".join(subject["notes"]))
    if elements["missing"]:
        must.append("缺三要素：%s" % "、".join(elements["missing"]))
    if conflicts:
        must.append("互斥/堆叠词：%s" % "；".join(conflicts))

    score = 100
    score -= min(24, 8 * len(neg_hits))
    score -= min(15, 5 * len(quality))
    score -= length["deduct"]
    score -= subject["deduct"]
    score -= elements["deduct"]
    score -= min(18, 6 * len(conflicts))
    score -= min(15, 5 * len(repeats))
    score = max(0, score)

    verdict = "可提交" if score >= 85 and not must else "需修改"
    return {
        "lang": "zh",
        "len": length["n"],
        "length": length,
        "neg": neg_hits,
        "neg_skipped": neg_skipped,
        "quality": quality,
        "subject": subject,
        "elements": elements,
        "conflicts": conflicts,
        "repeats": repeats,
        "must": must,
        "score": score,
        "verdict": verdict,
    }


def render(label, r):
    is_en = r.get("lang") == "en"
    out = []
    out.append("=" * 58)
    out.append(label + ("（英文模式）" if is_en else ""))
    out.append("-" * 58)
    if is_en:
        target = "（目标 40~80 词）"
        out.append("[1] 词数：%d 词%s  %s" %
                   (r["len"], target, "OK" if r["length"]["ok"] else "需改"))
    else:
        target = "（编辑模式，上限 120）" if r["elements"]["edit"] else "（目标 60~120）"
        out.append("[1] 字数：%d 字%s  %s" %
                   (r["len"], target, "OK" if r["length"]["ok"] else "需改"))
    out.append("    %s" % r["length"]["msg"])

    if r["neg"]:
        out.append("[2] 否定词：%d 处  需改" % len(r["neg"]))
        for i, term, frag in r["neg"][:5]:
            out.append("    第 %d %s「%s」…上下文：%s" %
                       (i, "字符" if is_en else "字", term, frag))
    else:
        out.append("[2] 否定词：0 处  OK%s" %
                   ("（已忽略正常中文：%s）" % "、".join(sorted(set(r["neg_skipped"])))
                    if r["neg_skipped"] else ""))

    if r["quality"]:
        shown = "、".join("「%s」" % w for _i, w in r["quality"][:6])
        more = "，等 %d 个" % len(r["quality"]) if len(r["quality"]) > 6 else ""
        out.append("[3] 无效画质词：%d 处  需改 → %s%s" % (len(r["quality"]), shown, more))
    else:
        out.append("[3] 无效画质词：0 处  OK")

    s = r["subject"]
    out.append("[4] 主体第一句%s：%s  首句：%s" %
               ("（参考图编辑，看“生成”之后）" if s["mode"] != "普通" else "",
                "OK" if s["ok"] else ("位置错" if s["fail"] else "缺动作"), s["first"]))
    for n in s["notes"]:
        out.append("    - %s" % n)

    e = r["elements"]
    out.append("[5] %s：画幅 %s ｜ 镜头 %s ｜ 光线 %s" %
               ("三要素（编辑模式，沿用参考图）" if e["edit"] else "三要素",
                "OK" if e["fig"] else "缺", "OK" if e["lens"] else "缺",
                "OK" if e["light"] else "缺"))
    for m in e["missing"]:
        out.append("    - 缺 %s" % m)

    if r["conflicts"]:
        out.append("[6] 互斥/堆叠：%s" % "；".join(r["conflicts"]))
    elif r["repeats"]:
        out.append("[6] 重复用词：%s" % "；".join(r["repeats"]))
    else:
        out.append("[6] 互斥/堆叠：0 处  OK")

    out.append("-" * 58)
    out.append("得分：%d ／ 结论：%s" % (r["score"], r["verdict"]))
    if r["must"]:
        out.append("必须改：")
        for m in r["must"]:
            out.append("  - %s" % m)
    return "\n".join(out)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

    ap = argparse.ArgumentParser(
        description="PromptLab 提示词自检（中/英，无第三方依赖）")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("-p", "--prompt", help="直接给一段提示词")
    group.add_argument("-f", "--file", help="从文件读一整段提示词")
    group.add_argument("-b", "--batch", help="批量：文件每行一条")
    ap.add_argument("--lang", choices=("zh", "en", "auto"), default="auto",
                    help="语言：zh 中文 / en 英文 / auto 自动判定（默认 auto）")
    args = ap.parse_args(argv)

    if args.prompt is not None:
        items = [(None, args.prompt)]
    elif args.file is not None:
        items = [(None, read_text_file(args.file))]
    elif args.batch is not None:
        lines = read_text_file(args.batch).splitlines()
        items = [("第 %d 行" % (i + 1), ln) for i, ln in enumerate(lines)
                 if ln.strip() and not ln.lstrip().startswith("#")]
        if not items:
            print("[错误] 批量文件里没有有效提示词：%s" % args.batch)
            return 2
    else:
        data = sys.stdin.buffer.read()
        for enc in ("utf-8-sig", "gbk", "utf-16"):
            try:
                text = data.decode(enc)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        else:
            text = ""
        if not text.strip():
            ap.print_usage()
            print("[错误] 没有输入：用 -p \"提示词\" / -f 文件 / -b 批量文件，或通过管道传入。")
            return 2
        items = [(None, text)]

    bad = 0
    for label, text in items:
        r = inspect(text, args.lang)
        if r["verdict"] != "可提交":
            bad += 1
        print(render(label or "提示词", r))

    if len(items) > 1:
        print("=" * 58)
        print("批量结果：共 %d 条，可提交 %d 条，需修改 %d 条。"
              % (len(items), len(items) - bad, bad))
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
