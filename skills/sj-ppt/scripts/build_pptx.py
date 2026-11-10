#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sj-ppt PPTX 生成器：deck.json -> 原生 .pptx（与 HTML 版同一决策器）
用法: python build_pptx.py deck.json out.pptx
"""
import json
import os
import sys
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.oxml.ns import qn

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
P15_NS = "http://schemas.microsoft.com/office/powerpoint/2015/09/main"

SX = 13.333 / 1280  # 舞台像素 -> 英寸


def C(h):
    h = h.lstrip("#")
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def mix(a, b, t):
    return RGBColor(int(a[0] * (1 - t) + b[0] * t),
                    int(a[1] * (1 - t) + b[1] * t),
                    int(a[2] * (1 - t) + b[2] * t))


BASE = dict(
    radius=0.10,
    serif="SimSun",
    sans="微软雅黑",
    fs_hero=60, fs_title=34, fs_h3=20, fs_body=14,
    fs_small=12, fs_micro=10, fs_kicker=13, fs_kpi=40,
    pad_x=96, pad_y=48, lead=1.7, tracking=-0.01,
    motion=0.6, stagger=90,
)

STYLES = {
    "claude-warm": dict(BASE, bg="#FAF9F5", surface="#FFFFFF", surface_alt="#F3F1EA",
                        ink="#1A1A18", muted="#6B6862", accent="#D97757", line="#E5E2DA", on_accent="#FFFFFF"),
    "tech-dark": dict(BASE, bg="#111315", surface="#181B1E", surface_alt="#1E2226",
                      ink="#F2F3F2", muted="#8A9095", accent="#3FBDB2", line="#262A2E", on_accent="#08110F"),

    "keynote": dict(BASE, bg="#0B0B0C", surface="#131316", surface_alt="#1D1D20",
                    ink="#F5F5F7", muted="#86868B", accent="#2997FF", line="#232327", on_accent="#FFFFFF",
                    radius=0, serif="微软雅黑", fs_hero=104, fs_title=46, fs_h3=24, fs_body=16, fs_small=13,
                    fs_micro=11, fs_kicker=12, fs_kpi=64, pad_x=110, pad_y=60, lead=1.5,
                    tracking=-0.03, motion=1.1, stagger=120),

    "academic": dict(BASE, bg="#FFFFFF", surface="#FFFFFF", surface_alt="#F4F6F8",
                     ink="#1B3A5C", muted="#5D6B7A", accent="#1B3A5C", line="#D9DFE6", on_accent="#FFFFFF",
                     radius=0.02, fs_hero=46, fs_title=28, fs_h3=18, fs_body=13, fs_small=11,
                     fs_micro=9.5, fs_kicker=11, fs_kpi=32, pad_x=88, pad_y=44, lead=1.65,
                     tracking=-0.01, motion=0.6, stagger=80),

    "consulting": dict(BASE, bg="#F7F7F5", surface="#FFFFFF", surface_alt="#EFEFEC",
                       ink="#16181D", muted="#6A6E73", accent="#B0432F", line="#DCDBD5", on_accent="#FFFFFF",
                       radius=0, serif="微软雅黑", fs_hero=44, fs_title=24, fs_h3=16, fs_body=12, fs_small=10.5,
                       fs_micro=9, fs_kicker=10, fs_kpi=30, pad_x=64, pad_y=40, lead=1.55,
                       tracking=-0.01, motion=0.55, stagger=80),

    "contest": dict(BASE, bg="#FFFFFF", surface="#FFFFFF", surface_alt="#F3F2EE",
                    ink="#111114", muted="#6B6E75", accent="#FF3D00", line="#E7E5DF", on_accent="#FFFFFF",
                    radius=0, fs_hero=88, fs_title=42, fs_h3=24, fs_body=15, fs_small=12,
                    fs_micro=10, fs_kicker=12, fs_kpi=76, pad_x=104, pad_y=56, lead=1.6,
                    tracking=-0.03, motion=0.85, stagger=110),

    "minimal-art": dict(BASE, bg="#F2EFE9", surface="#F2EFE9", surface_alt="#E8E3D9",
                        ink="#1E1C18", muted="#7A736A", accent="#A65C3B", line="#D8D1C4", on_accent="#F7F4EE",
                        radius=0, fs_hero=64, fs_title=34, fs_h3=22, fs_body=13, fs_small=11,
                        fs_micro=9, fs_kicker=10, fs_kpi=40, pad_x=96, pad_y=56, lead=1.75,
                        tracking=-0.02, motion=0.78, stagger=100),
}

LABEL = {"keynote": "苹果发布会", "academic": "学术答辩", "consulting": "咨询研报",
         "contest": "国赛获奖", "minimal-art": "极简美术",
         "claude-warm": "暖白", "tech-dark": "科技深色"}


def pt(px):
    return Pt(px * 0.72)


def inch(px):
    return Inches(px * SX)


def text_len(p):
    bits = [p.get("title"), p.get("subtitle"), p.get("kicker"), p.get("caption"),
            p.get("note"), p.get("label"), p.get("text")]
    bits += [(x.get("title") or "") + (x.get("text") or "") for x in p.get("items", [])]
    bits += [(x.get("name") or "") + (x.get("code") or "") + (x.get("desc") or "") for x in p.get("cards", [])]
    bits += [x.get("label") or "" for x in p.get("parts", [])]
    return len("".join([b for b in bits if b]))


def analyze(deck):
    pages = deck.get("slides", [])
    n = len(pages)
    charts = len([p for p in pages if p.get("chart") and p["chart"].get("values")])
    ratio = charts / n if n else 0
    avg = sum(text_len(p) for p in pages) / n if n else 0
    density = "低" if avg < 120 else ("中" if avg < 240 else "高")
    has_concl = any(("结论" in (p.get("title") or "")) or ("总结" in (p.get("title") or ""))
                    or (i == n - 1 and p.get("type") == "end") for i, p in enumerate(pages))
    return dict(pageCount=n, chartRatio=ratio, density=density, hasConclusion=has_concl, avg=avg)


KEYWORD_RULES = [
    ("academic", ["答辩", "结题", "实验", "论文", "课程", "汇报", "大创"]),
    ("contest", ["路演", "创业", "挑战杯", "互联网+", "竞赛", "大赛", "比赛"]),
    ("keynote", ["发布", "新品", "产品", "创意", "demo", "Demo", "展示", "亮相"]),
    ("consulting", ["数据分析", "调研", "复盘", "评估", "报告", "研究"]),
]


def pick_style(deck):
    m = deck.get("meta", {}) or {}
    pages = deck.get("slides", [])
    info = analyze(deck)
    page_count = int(m.get("pageCount") or info["pageCount"])
    ratio = m.get("chartRatio") if isinstance(m.get("chartRatio"), (int, float)) else info["chartRatio"]
    density = m.get("textDensity") or info["density"]
    purpose = m.get("purpose", "") or ""
    rt = f"{ratio:.2f}"

    forced = None
    if isinstance(m.get("style"), str) and m["style"] in STYLES:
        forced = m["style"]
    if isinstance(deck.get("style"), str) and deck["style"] in STYLES:
        forced = deck["style"]
    if forced:
        return forced, f"meta.style={forced} 已强制指定 → {forced}（{LABEL[forced]}）"

    if isinstance(deck.get("theme"), str) and deck["theme"] in STYLES:
        return deck["theme"], f"旧字段 theme={deck['theme']} 直接采用"
    if isinstance(deck.get("theme"), dict):
        return "claude-warm", "theme 为颜色覆盖对象，沿用 claude-warm 结构"

    if any(k in purpose for k in ("作品集", "展示", "汇报")) and density == "低" and page_count <= 12:
        return "minimal-art", (f"purpose={purpose}（命中「作品集/展示/汇报」）、文本密度 {density}、"
                             f"{page_count} 页 ≤ 12 → minimal-art（极简美术）")

    hay = " ".join([purpose, deck.get("title", "")] +
                   [(p.get("title") or "") for p in pages] + [(p.get("kicker") or "") for p in pages])
    hit = None
    for name, words in KEYWORD_RULES:
        for w in words:
            if w in hay:
                hit = (name, w)
                break
        if hit:
            break
    if hit:
        return hit[0], (f"检测到 purpose={purpose or '（未填）'}（关键词命中「{hit[1]}」）、"
                        f"图表占比 {rt} → {hit[0]}（{LABEL[hit[0]]}）")

    if ratio > 0.4 and density == "高":
        return "consulting", f"特征打分：图表占比 {rt} > 0.4 且文本密度 {density} → consulting（咨询研报）"
    if page_count <= 10 and density == "低" and ratio >= 0.3:
        return "keynote", (f"特征打分：{page_count} 页 ≤ 10、文本密度 {density}、"
                           f"图表占比 {rt} → keynote（苹果发布会）")
    if page_count >= 15 and info["hasConclusion"]:
        return "academic", f"特征打分：{page_count} 页 ≥ 15 且有结论页 → academic（学术答辩）"
    return "contest", (f"特征打分：图表占比 {rt}、文本密度 {density}、{page_count} 页 → "
                       f"默认 contest（国赛获奖）")


# ---------------- 基础绘制 ----------------------------


def bg(slide, th):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = C(th["bg"])


def tx(slide, x, y, w, h, text, th, size, color, bold=False, font=None,
       align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0, italic=False):
    box = slide.shapes.add_textbox(inch(x), inch(y), inch(w), inch(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.name = font or th["sans"]
        r.font.color.rgb = color
    return box


def rect(slide, x, y, w, h, th, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, radius=None):
    sp = slide.shapes.add_shape(shape, inch(x), inch(y), inch(w), inch(h))
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid()
        sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = Pt(lw)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sp.adjustments[0] = radius
        except Exception:
            pass
    return sp


def line_h(slide, x, y, w, th, color=None, lw=0.75):
    sp = slide.shapes.add_connector(1, inch(x), inch(y), inch(x + w), inch(y))
    sp.line.color.rgb = color or C(th["line"])
    sp.line.width = Pt(lw)
    return sp


def add_footer(slide, th, idx, total, deck, style):
    m = th["pad_x"]
    if style == "academic":
        label = deck.get("footer") or (deck.get("meta") or {}).get("audience") or ""
        if label:
            tx(slide, m, 690, 700, 18, label, th, th["fs_micro"], C(th["muted"]))
        tx(slide, 1180 - m, 686, 100, 20, f"{idx:02d} / {total:02d}", th, th["fs_micro"], C(th["muted"]),
           align=PP_ALIGN.RIGHT)
    elif style == "consulting":
        tx(slide, 1180 - m, 686, 110, 20, f"EXHIBIT {idx:02d}", th, th["fs_micro"], C(th["muted"]),
           align=PP_ALIGN.RIGHT)
    elif style == "minimal-art":
        tx(slide, 1180 - m, 686, 100, 20, f"{idx:02d} / {total:02d}", th, th["fs_micro"], C(th["muted"]),
           align=PP_ALIGN.RIGHT)
    else:
        tx(slide, 1180 - m, 688, 90, 18, f"{idx:02d}", th, th["fs_micro"], C(th["muted"]),
           align=PP_ALIGN.RIGHT)


def add_picture_bg(slide, path, fit="cover"):
    try:
        from PIL import Image
        with Image.open(path) as im:
            iw, ih = im.size
        if fit == "contain":
            k = min(13.333 / iw, 7.5 / ih)
            w, h = iw * k, ih * k
            slide.shapes.add_picture(path, Inches((13.333 - w) / 2), Inches((7.5 - h) / 2),
                                     width=Inches(w), height=Inches(h))
        else:
            slide.shapes.add_picture(path, 0, 0, width=Inches(13.333), height=Inches(7.5))
        return True
    except Exception as e:
        print(f"[sj-ppt] 图片嵌入失败: {path} ({e})")
        return False


def tint(th, color_key, amount):
    return mix(C(th["bg"]), C(th[color_key]), amount)


# ---------------- 页面 ----------------------------


def build_cover(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    if pic and add_picture_bg(slide, pic, s.get("artFit", "cover")):
        return []
    m = th["pad_x"]
    ids = []
    if style == "keynote":
        top = 232
        w = 1010
    elif style == "contest":
        top = 150
        w = 1000
    elif style == "consulting":
        top = 150
        w = 1020
        rect(slide, m - 26, top + 10, 6, 120, th, fill=C(th["accent"]))
    elif style == "minimal-art":
        top = 200
        w = 900
    else:
        top = 170
        w = 940

    kicker = s.get("kicker", "")
    if kicker:
        tx(slide, m, top - 48, w, 30, kicker, th, th["fs_kicker"], C(th["accent"]), bold=True, spacing=1.0)
    title_size = th["fs_hero"] * (0.78 if style == "keynote" else 1.0)
    title_box = tx(slide, m, top, w, 300, s.get("title", ""), th, title_size, C(th["ink"]),
                   bold=(style in ("keynote", "contest", "consulting")), font=th["serif"],
                   spacing=1.08)
    ids.append(title_box)

    ry = top + 300 if style != "keynote" else 430
    line_h(slide, m, ry, 120, th, C(th["line"]), 1.2)
    rect(slide, m, ry - 1, 32, 3, th, fill=C(th["accent"]))

    if s.get("subtitle"):
        tx(slide, m, ry + 30, 760, 90, s["subtitle"], th, th["fs_body"] * 1.3, C(th["muted"]), spacing=1.5)
    tags = s.get("tags") or []
    if tags:
        tx(slide, m, 606, 900, 30, "    ".join(tags), th, th["fs_micro"], C(th["muted"]), spacing=1.2)
    meta = " ".join([x for x in [deck.get("presenter", ""), deck.get("date", "")] if x])
    if meta:
        tx(slide, 1180 - m, 600, 200, 24, meta, th, th["fs_micro"], C(th["muted"]), align=PP_ALIGN.RIGHT)
    return ids


def build_statement(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    if pic and add_picture_bg(slide, pic, s.get("artFit", "cover")):
        return []
    ids = []
    if s.get("kicker"):
        tx(slide, 180, 250, 920, 30, s["kicker"], th, th["fs_kicker"], C(th["accent"]),
           align=PP_ALIGN.CENTER, bold=True)
    tw = 1100 if style == "keynote" else 980
    t = tx(slide, (1280 - tw) / 2, 300, tw, 200, s.get("title", ""), th,
           th["fs_hero"] * (0.76 if style == "keynote" else 0.8), C(th["ink"]),
           bold=True, font=th["serif"], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.12)
    ids.append(t)
    if s.get("subtitle"):
        tx(slide, 240, 520, 800, 70, s["subtitle"], th, th["fs_body"] * 1.2, C(th["muted"]),
           align=PP_ALIGN.CENTER, spacing=1.5)
    return ids


def build_data(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    m = th["pad_x"]
    ids = []
    head = tx(slide, m, th["pad_y"], 1120, 90, s.get("title", ""), th, th["fs_title"], C(th["ink"]),
              bold=(style == "consulting"), font=th["serif"], spacing=1.2)
    ids.append(head)
    line_h(slide, m, th["pad_y"] + 92, 56, th, C(th["accent"]), 2.0)

    stats = (s.get("stats") or [])[:3]
    y0 = 210
    for k, st in enumerate(stats):
        yy = y0 + k * 132
        if style == "consulting":
            line_h(slide, m, yy, 300, th, C(th["line"]))
            tx(slide, m, yy + 10, 300, 26, str(st.get("label", "")), th, th["fs_small"], C(th["muted"]))
            tx(slide, m, yy + 38, 300, 60, f"{st.get('value','')}{st.get('unit','')}", th,
               th["fs_kpi"], C(th["ink"]), bold=True)
        elif style == "contest":
            rect(slide, m, yy, 4, 92, th, fill=C(th["accent"]))
            tx(slide, m + 20, yy - 2, 320, 64, f"{st.get('value','')}{st.get('unit','')}", th,
               th["fs_kpi"], C(th["ink"]), bold=True)
            tx(slide, m + 20, yy + 82, 320, 26, str(st.get("label", "")), th, th["fs_small"], C(th["muted"]))
        elif style == "minimal-art":
            rect(slide, m, yy, 1, 92, th, fill=C(th["line"]))
            tx(slide, m + 18, yy + 8, 300, 58, f"{st.get('value','')}{st.get('unit','')}", th,
               th["fs_kpi"], C(th["accent"]), font=th["serif"], spacing=1.1)
            tx(slide, m + 18, yy + 68, 300, 24, str(st.get("label", "")), th, th["fs_small"], C(th["muted"]))
        else:
            box = rect(slide, m, yy, 300, 108, th, fill=C(th["surface"]), line=C(th["line"]), lw=1,
                       shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=min(0.5, th["radius"]))
            tx(slide, m + 20, yy + 12, 260, 56, f"{st.get('value','')}{st.get('unit','')}", th,
               th["fs_kpi"], C(th["ink"]), bold=True)
            tx(slide, m + 20, yy + 70, 260, 26, str(st.get("label", "")), th, th["fs_small"], C(th["muted"]))
            ids.append(box)

    ch = s.get("chart")
    cx, cy, cw, chh = m + 350, 196, 1080 - m - 350, 390
    if ch:
        values = ch.get("values") or []
        labels = ch.get("labels") or []
        data = None
        try:
            from pptx.chart.data import CategoryChartData
            data = CategoryChartData()
            data.categories = labels
            data.add_series(ch.get("name", "数值"), values)
            gf = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, inch(cx), inch(cy), inch(cw), inch(chh), data)
            chart = gf.chart
            chart.has_legend = False
            chart.has_title = False
            plot = chart.plots[0]
            plot.gap_width = 55
            ser = plot.series[0]
            if style == "minimal-art":
                ser.format.fill.background()
                ser.format.line.color.rgb = C(th["ink"])
                ser.format.line.width = Pt(1.0)
            else:
                ser.format.fill.solid()
                ser.format.fill.fore_color.rgb = C(th["accent"])
            plot.has_data_labels = True
            dl = plot.data_labels
            dl.font.size = pt(th["fs_small"])
            dl.font.name = th["sans"]
            dl.font.color.rgb = C(th["accent"] if style == "minimal-art" else th["ink"])
            dl.position = XL_LABEL_POSITION.OUTSIDE_END
            if ch.get("unit"):
                dl.number_format = f'0"{ch["unit"]}"'
                dl.number_format_is_linked = False
            ca = chart.category_axis
            ca.has_major_gridlines = False
            ca.format.line.color.rgb = C(th["line"])
            ca.tick_labels.font.size = pt(th["fs_small"])
            ca.tick_labels.font.name = th["sans"]
            ca.tick_labels.font.color.rgb = C(th["muted"])
            va = chart.value_axis
            va.visible = False
            va.has_major_gridlines = False
            ids.append(gf)
        except Exception as e:
            print(f"[sj-ppt] 图表生成失败: {e}")
        if ch.get("caption"):
            tx(slide, cx, 610, cw, 24, ch["caption"], th, th["fs_micro"], C(th["muted"]), align=PP_ALIGN.CENTER)
    if s.get("note"):
        tx(slide, m, 650, 700, 24, s["note"], th, th["fs_micro"], C(th["muted"]))
    add_footer(slide, th, idx, len(deck.get("slides", [])), deck, style)
    return ids


def build_points(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    m = th["pad_x"]
    ids = []
    head = tx(slide, m, th["pad_y"], 1100, 90, s.get("title", ""), th, th["fs_title"], C(th["ink"]),
              bold=(style == "consulting"), font=th["serif"])
    ids.append(head)
    if style != "consulting":
        line_h(slide, m, th["pad_y"] + 92, 56, th, C(th["accent"]), 2.0)

    items = (s.get("items") or [])[:4]
    gap = 24
    cw = (1080 - m - m - gap) / 2
    chh = 190 if len(items) > 2 else 240
    for k, it in enumerate(items):
        col = k % 2
        row = k // 2
        x = m + col * (cw + gap)
        y = 200 + row * (chh + 24)
        card = rect(slide, x, y, cw, chh, th, fill=C(th["surface"]), line=C(th["line"]), lw=1,
                    shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=min(0.5, th["radius"]))
        if style in ("keynote", "minimal-art", "contest"):
            card.fill.background()
            card.line.fill.background()
            line_h(slide, x, y, cw, th, C(th["line"]), 1.0)
            if style == "contest":
                line_h(slide, x, y, cw, th, C(th["ink"]), 2.0)
        ids.append(card)
        tx(slide, x + 24, y + 20, cw - 48, 20, f"{k+1:02d}", th, th["fs_micro"], C(th["accent"]), bold=True)
        tx(slide, x + 24, y + 48, cw - 48, 36, it.get("title", ""), th, th["fs_h3"], C(th["ink"]),
           bold=True, font=th["serif"])
        tx(slide, x + 24, y + 94, cw - 48, chh - 110, it.get("text", ""), th, th["fs_body"],
           C(th["muted"]), spacing=th["lead"] * 0.85)
    add_footer(slide, th, idx, len(deck.get("slides", [])), deck, style)
    return ids


PART_SPEC = {
    "endcap": (70, 190), "flange": (96, 210), "gasket": (14, 180), "bolt": (30, 160)
}


def build_exploded(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    m = th["pad_x"]
    ids = []
    head = tx(slide, m, th["pad_y"], 1100, 70, s.get("title", ""), th, th["fs_title"], C(th["ink"]),
              bold=(style == "consulting"), font=th["serif"])
    ids.append(head)
    line_h(slide, m, th["pad_y"] + 72, 56, th, C(th["accent"]), 2.0)

    parts = (s.get("parts") or [])[:6]
    n = len(parts)
    gap = 20
    widths = [PART_SPEC.get(p.get("kind"), PART_SPEC["flange"])[0] for p in parts]
    total = sum(widths) + gap * (n - 1)
    cx = 640 - total / 2
    cy = 390
    for k, p in enumerate(parts):
        kind = p.get("kind")
        w, h = PART_SPEC.get(kind, PART_SPEC["flange"])
        x = cx
        y = cy - h / 2
        if kind == "flange":
            shp = rect(slide, x, y, w, h, th, fill=C(th["surface_alt"]), line=C(th["ink"]), lw=1.2,
                       shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
            for hx, hy in ((-(w/2-18), -(h/2-30)), (w/2-18, -(h/2-30)), (-(w/2-18), h/2-30), (w/2-18, h/2-30)):
                rect(slide, x + w/2 + hx - 6, y + h/2 + hy - 6, 12, 12, th, fill=C(th["bg"]),
                     line=C(th["ink"]), lw=1, shape=MSO_SHAPE.OVAL)
        elif kind == "gasket":
            shp = rect(slide, x, y, w, h, th, fill=tint(th, "accent", 0.18), line=C(th["accent"]), lw=1)
        elif kind == "bolt":
            shp = rect(slide, x, y + 40, w, h - 40, th, fill=C(th["surface"]), line=C(th["ink"]), lw=1,
                       shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.18)
            rect(slide, x + w/2 - 15, y + 12, 30, 30, th, fill=C(th["surface"]), line=C(th["ink"]), lw=1,
                 shape=MSO_SHAPE.OVAL)
        else:
            shp = rect(slide, x, y, w, h, th, fill=C(th["surface_alt"]), line=C(th["ink"]), lw=1.2,
                       shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.12)
            rect(slide, x + w/2 - 18, y + h/2 - 58, 36, 116, th, fill=C(th["bg"]), line=C(th["line"]), lw=1,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08)
        ids.append(shp)

        lx = x + w / 2
        line_h(slide, lx, 120, 0.01, th, C(th["line"]), 1.0)
        c = slide.shapes.add_connector(1, inch(lx), inch(y - 24), inch(lx), inch(y - 60))
        c.line.color.rgb = C(th["line"])
        c.line.width = Pt(0.75)
        tx(slide, lx - 60, 74, 120, 22, f"{k+1:02d}", th, 13, C(th["accent"]), bold=True, align=PP_ALIGN.CENTER)
        tx(slide, lx - 70, 96, 140, 24, p.get("label", ""), th, 15, C(th["ink"]), align=PP_ALIGN.CENTER)
        cx += w + gap

    tx(slide, m, 612, 760, 40, s.get("caption", ""), th, th["fs_small"], C(th["muted"]), spacing=1.3)
    if style != "keynote":
        tx(slide, 700, 650, 380, 24, "pptx 版：静态分解排布 + 分步出现（无反向合拢）",
           th, th["fs_micro"], C(th["muted"]), align=PP_ALIGN.RIGHT)
    add_footer(slide, th, idx, len(deck.get("slides", [])), deck, style)
    return ids


def build_materials(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    m = th["pad_x"]
    ids = []
    head = tx(slide, m, th["pad_y"], 1100, 70, s.get("title", ""), th, th["fs_title"], C(th["ink"]),
              bold=(style == "consulting"), font=th["serif"])
    ids.append(head)
    line_h(slide, m, th["pad_y"] + 72, 56, th, C(th["accent"]), 2.0)

    cards = (s.get("cards") or [])[:3]
    n = len(cards)
    gap = 24
    cw = (1080 - m - m - gap * (n - 1)) / n
    for k, c in enumerate(cards):
        x = m + k * (cw + gap)
        y = 190
        chh = 400
        card = rect(slide, x, y, cw, chh, th, fill=C(th["surface"]), line=C(th["line"]), lw=1)
        ids.append(card)
        sw = rect(slide, x + 1, y + 1, cw - 2, 200, th, fill=C(th["surface_alt"]), line=None)
        kind = c.get("kind")
        if kind == "brushed":
            for j in range(9):
                yy = y + 40 + j * 16
                line_h(slide, x + 20, yy, cw - 40, th, mix(C("#EEEBE3"), C("#BDB8AE"), j / 8), 1.0)
        elif kind == "anodized":
            rect(slide, x + 1, y + 1, cw - 2, 200, th, fill=C("#2C3136"), line=None)
            rect(slide, x + 1, y + 1, cw - 2, 54, th, fill=C("#3A4046"), line=None)
            for j in range(6):
                rect(slide, x + 30 + j * (cw - 60) / 6, y + 80 + (j % 2) * 30, 3, 3, th,
                     fill=C("#4B5157"), line=None, shape=MSO_SHAPE.OVAL)
        else:
            rect(slide, x + 1, y + 1, cw - 2, 200, th, fill=C("#0E372A"), line=None)
            for j in range(3):
                yy = y + 50 + j * 42
                rect(slide, x + 20, yy, cw - 50, 3, th, fill=C("#C9A05A"), line=None)
            rect(slide, x + 28, y + 45, 3, 90, th, fill=C("#C9A05A"), line=None)
        line_h(slide, x, y + 201, cw, th, C(th["line"]))

        tx(slide, x + 22, y + 218, cw - 44, 30, f"{k+1:02d}", th, th["fs_micro"], C(th["muted"]))
        tx(slide, x + 22, y + 244, cw - 44, 34, c.get("name", ""), th, th["fs_h3"], C(th["ink"]),
           bold=True, font=th["serif"])
        tx(slide, x + 22, y + 280, cw - 44, 22, c.get("code", ""), th, th["fs_micro"], C(th["muted"]))
        tx(slide, x + 22, y + 306, cw - 44, 70, c.get("desc", ""), th, th["fs_small"], C(th["muted"]),
           spacing=th["lead"] * 0.8)
    if s.get("caption"):
        tx(slide, m, 612, 700, 30, s["caption"], th, th["fs_micro"], C(th["muted"]))
    tx(slide, 700, 650, 380, 24, "pptx 版：材质静态示意（扫光/切换/放大见 HTML 版）",
       th, th["fs_micro"], C(th["muted"]), align=PP_ALIGN.RIGHT)
    add_footer(slide, th, idx, len(deck.get("slides", [])), deck, style)
    return ids


def build_end(prs, slide, s, th, idx, deck, style, pic):
    bg(slide, th)
    if pic and add_picture_bg(slide, pic, s.get("artFit", "cover")):
        return []
    ids = []
    if style == "minimal-art":
        ring = slide.shapes.add_shape(MSO_SHAPE.OVAL, inch(592), inch(160), inch(96), inch(96))
        ring.fill.background()
        ring.line.color.rgb = C(th["accent"])
        ring.line.width = Pt(1)
        ring.shadow.inherit = False
    t = tx(slide, 140, 300, 1000, 120, s.get("title", ""), th, th["fs_hero"] * 0.8, C(th["ink"]),
           bold=False, font=th["serif"], align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE, spacing=1.15)
    ids.append(t)
    if s.get("subtitle"):
        tx(slide, 240, 448, 800, 60, s["subtitle"], th, th["fs_body"], C(th["muted"]),
           align=PP_ALIGN.CENTER, spacing=1.4)
    add_footer(slide, th, idx, len(deck.get("slides", [])), deck, style)
    return ids


BUILDERS = {
    "cover": build_cover, "statement": build_statement, "data": build_data,
    "points": build_points, "exploded": build_exploded,
    "materials": build_materials, "end": build_end
}


def add_transition_morph(slide):
    tr = etree.SubElement(slide.element, qn("p:transition"))
    morph = etree.SubElement(tr, f"{{{P15_NS}}}morph")
    morph.set("option", "byObject")


def add_timing(slide, shape_ids):
    if not shape_ids:
        return
    timing = etree.SubElement(slide.element, qn("p:timing"))
    tn = etree.SubElement(timing, qn("p:tnLst"))
    par0 = etree.SubElement(tn, qn("p:par"))
    ctn1 = etree.SubElement(par0, qn("p:cTn"), id="1", dur="indefinite", restart="never", nodeType="tmRoot")
    c1 = etree.SubElement(ctn1, qn("p:childTnLst"))
    seq = etree.SubElement(c1, qn("p:seq"), concurrent="1", nextAc="seek")
    ctn2 = etree.SubElement(seq, qn("p:cTn"), id="2", dur="indefinite", nodeType="mainSeq")
    c2 = etree.SubElement(ctn2, qn("p:childTnLst"))
    nid = 3
    for sid in shape_ids:
        a = etree.SubElement(c2, qn("p:par"))
        ca = etree.SubElement(a, qn("p:cTn"), id=str(nid), fill="hold")
        nid += 1
        etree.SubElement(ca, qn("p:stCondLst"))
        ca.find(qn("p:stCondLst")).append(etree.Element(qn("p:cond"), delay="indefinite"))
        cbl = etree.SubElement(ca, qn("p:childTnLst"))
        b = etree.SubElement(cbl, qn("p:par"))
        cb = etree.SubElement(b, qn("p:cTn"), id=str(nid), fill="hold")
        nid += 1
        etree.SubElement(cb, qn("p:stCondLst"))
        cb.find(qn("p:stCondLst")).append(etree.Element(qn("p:cond"), delay="0"))
        ccl = etree.SubElement(cb, qn("p:childTnLst"))
        d = etree.SubElement(ccl, qn("p:par"))
        cd = etree.SubElement(d, qn("p:cTn"), id=str(nid), presetID="10", presetClass="entr",
                              presetSubtype="0", fill="hold", nodeType="clickEffect")
        nid += 1
        etree.SubElement(cd, qn("p:stCondLst"))
        cd.find(qn("p:stCondLst")).append(etree.Element(qn("p:cond"), delay="0"))
        cdl = etree.SubElement(cd, qn("p:childTnLst"))
        st = etree.SubElement(cdl, qn("p:set"))
        cb2 = etree.SubElement(st, qn("p:cBhvr"))
        etree.SubElement(cb2, qn("p:cTn"), id=str(nid), dur="1", fill="hold")
        nid += 1
        cb2.find(qn("p:cTn")).append(etree.Element(qn("p:stCondLst")))
        cb2.find(qn("p:cTn")).find(qn("p:stCondLst")).append(etree.Element(qn("p:cond"), delay="0"))
        tg = etree.SubElement(cb2, qn("p:tgtEl"))
        etree.SubElement(tg, qn("p:spTgt"), spid=str(sid))
        an = etree.SubElement(cb2, qn("p:attrNameLst"))
        etree.SubElement(an, qn("p:attrName")).text = "style.visibility"
        to = etree.SubElement(st, qn("p:to"))
        etree.SubElement(to, qn("p:strVal"), val="visible")
    prev = etree.SubElement(ctn2, qn("p:prevCondLst"))
    pc = etree.SubElement(prev, qn("p:cond"), evt="onPrev", delay="0")
    etree.SubElement(etree.SubElement(pc, qn("p:tgtEl")), qn("p:sldTgt"))
    nxt = etree.SubElement(ctn2, qn("p:nextCondLst"))
    nc = etree.SubElement(nxt, qn("p:cond"), evt="onNext", delay="0")
    etree.SubElement(etree.SubElement(nc, qn("p:tgtEl")), qn("p:sldTgt"))


def main():
    if len(sys.argv) < 3:
        print("用法: python build_pptx.py deck.json out.pptx")
        sys.exit(1)
    in_path, out_path = sys.argv[1], sys.argv[2]
    deck = json.load(open(in_path, encoding="utf-8"))
    deck_dir = os.path.dirname(os.path.abspath(in_path))
    style, reason = pick_style(deck)
    th = STYLES[style]
    pages = deck.get("slides", [])

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    for i, s in enumerate(pages):
        page_style = s.get("styleOverride") if s.get("styleOverride") in STYLES else style
        pth = STYLES[page_style]
        slide = prs.slides.add_slide(blank)
        art = s.get("art")
        pic = None
        if art:
            pic = art if os.path.isabs(art) else os.path.join(deck_dir, art)
            if not os.path.exists(pic):
                print(f"[sj-ppt] 找不到图片: {pic}")
                pic = None
        build = BUILDERS.get(s.get("type"), build_points)
        ids = build(prs, slide, s, pth, i + 1, deck, page_style, pic)
        shape_ids = [int(sh.shape_id) for sh in ids if sh is not None]
        add_transition_morph(slide)
        add_timing(slide, shape_ids)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    prs.save(out_path)
    print(f"PPTX 已生成: {out_path}（{len(pages)} 页，风格 {style}｜{LABEL[style]}）")
    print(f"风格理由: {reason}")


if __name__ == "__main__":
    main()
