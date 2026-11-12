#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
coordinate-plot / 坐标纸出图
把实验数据画成"毫米方格纸"风格的曲线图，供打印后手绘抄图。

核心约束：图上的网格是真实毫米。y 轴 1 小格 = 1 mm，10 小格 = 1 大格，
          因此整张图的物理尺寸由"大格个数"决定，不能再用 bbox_inches='tight'。
"""

import argparse
import csv
import math
import os
import sys
from datetime import datetime

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, rcParams

MM = 1.0 / 25.4  # 毫米 -> 英寸

# 中文字体优先顺序：Windows 自带 -> macOS -> Linux/.trae 环境
FONT_CANDIDATES = [
    "Microsoft YaHei",     # Windows 10/11
    "SimHei",              # Windows 黑体
    "SimSun",              # Windows 宋体
    "Noto Sans CJK SC",    # Linux 常见
    "Source Han Sans SC",  # Linux 常见
    "WenQuanYi Zen Hei",   # Linux 常见
    "PingFang SC",         # macOS
    "Heiti SC",            # macOS
    "Arial Unicode MS",    # macOS 兜底
    "DejaVu Sans",         # 最后兜底：补 ⁻ ¹ ² 等上标符号
]

GRID_MINOR = dict(color="#b0b0b0", lw=0.38)
GRID_MID = dict(color="#777777", lw=0.60)
GRID_MAJOR = dict(color="#1a1a1a", lw=0.90)

INK = "#000000"
COLORS = ["#000000", "#b8332f", "#1f5fa8", "#2b7a3d", "#7b4a9c", "#b8770f"]
MARKERS = ["o", "s", "^", "D", "v", "P"]


# ----------------------------------------------------------------------------
# 字体
# ----------------------------------------------------------------------------
def setup_font(preferred=None):
    """挑一个系统里真实存在的中文字体，并把缺字时的回退链写进 rcParams。"""
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    if preferred:
        if preferred in available:
            chosen = preferred
        else:
            print("[warn] 指定字体 %r 不存在，改用自动选择" % preferred, file=sys.stderr)
    if chosen is None:
        for name in FONT_CANDIDATES:
            if name in available:
                chosen = name
                break
    if chosen is None:
        print("[warn] 没找到中文字体，图中中文会变成方块。"
              "请用 --font 指定一个已安装的中文字体。", file=sys.stderr)
        chosen = "DejaVu Sans"

    # 注意：这里必须给 font.family 一个"字体族列表"，matplotlib 才会做逐字回退；
    # 只写 'sans-serif' 这种别名时，缺字不会回退，会直接报警并画空框。
    # 列表里只放本机真实存在的字体，否则 findfont 会刷屏。
    chain = [chosen] + [n for n in FONT_CANDIDATES if n != chosen and n in available]
    rcParams["font.family"] = chain
    rcParams["font.sans-serif"] = chain
    rcParams["axes.unicode_minus"] = False   # 负号用 ASCII，避免缺字形
    rcParams["pdf.fonttype"] = 42
    rcParams["svg.fonttype"] = "none"
    return chosen


# ----------------------------------------------------------------------------
# 数据读取
# ----------------------------------------------------------------------------
def _to_float(s):
    try:
        return float(str(s).strip())
    except (TypeError, ValueError):
        return None


def read_csv(path, x_col, y_cols, force_header=None, delimiter=None):
    """读 CSV，返回 (x_array, [y_array, ...], 列名列表)。

    x_col / y_cols 既可以是列名，也可以是 0 起的列序号字符串。
    """
    if not os.path.isfile(path):
        raise SystemExit("[error] 找不到数据文件: %s" % path)

    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(4096)
        f.seek(0)
        if delimiter and delimiter != "auto":
            delim = delimiter
        else:
            try:
                delim = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
            except csv.Error:
                delim = ","
        rows = [r for r in csv.reader(f, delimiter=delim) if any(c.strip() for c in r)]

    if not rows:
        raise SystemExit("[error] 数据文件是空的: %s" % path)

    first = [_to_float(c) for c in rows[0]]
    if force_header is True:
        has_header = True
    elif force_header is False:
        has_header = False
    else:
        has_header = not all(v is not None for v in first)

    header = [c.strip() for c in rows[0]] if has_header else []
    body = rows[1:] if has_header else rows
    ncol = max(len(r) for r in rows)

    def resolve(col, kind):
        if col is None:
            raise SystemExit("[error] 缺少 %s 列参数（--x / --y）" % kind)
        col = str(col).strip()
        if has_header and col in header:
            return header.index(col)
        if col.lstrip("-").isdigit():
            idx = int(col)
            if 0 <= idx < ncol:
                return idx
        raise SystemExit(
            "[error] 找不到列 %r。文件 %s 可用列: %s"
            % (col, os.path.basename(path),
               ", ".join(header) if header else "0..%d（无表头）" % (ncol - 1))
        )

    xi = resolve(x_col, "x")
    yi = [resolve(c, "y") for c in y_cols]

    xs, ys = [], [[] for _ in yi]
    for r in body:
        if len(r) <= max([xi] + yi):
            continue
        xv = _to_float(r[xi])
        yv = [_to_float(r[i]) for i in yi]
        if xv is None or any(v is None for v in yv):
            continue  # 空行/缺测点直接跳过
        xs.append(xv)
        for k, v in enumerate(yv):
            ys[k].append(v)

    if not xs:
        raise SystemExit("[error] %s 里没有可用的数值行" % path)

    x = np.asarray(xs, dtype=float)
    y_arr = [np.asarray(v, dtype=float) for v in ys]

    order = np.argsort(x, kind="stable")
    x = x[order]
    y_arr = [v[order] for v in y_arr]

    names = [header[i] if has_header and i < len(header) else "col%d" % i for i in [xi] + yi]
    return x, y_arr, names, xi, yi


# ----------------------------------------------------------------------------
# 刻度 / 范围
# ----------------------------------------------------------------------------
def _candidates():
    out = []
    for e in range(-9, 10):
        for m in (1.0, 2.0, 2.5, 5.0):
            out.append(m * (10.0 ** e))
    return sorted(out)


def pick_step(span, target=9.0, min_div=4, max_div=12):
    """选一个"好看"的刻度间隔，使大格数落在 [min_div, max_div]。"""
    if span <= 0:
        return 1.0
    cands = _candidates()
    ok = [c for c in cands if min_div - 1e-9 <= span / c <= max_div + 1e-9]
    if ok:
        return min(ok, key=lambda c: (abs(span / c - target), c))
    return min(cands, key=lambda c: abs(span / c - target))


def snap(lo, hi, step):
    """把范围吸附到 step 的整数倍上——这样 0 一定落在网格线上，刻度不会错位。"""
    lo_s = math.floor(lo / step + 1e-9) * step
    hi_s = math.ceil(hi / step - 1e-9) * step
    if hi_s - lo_s < step * 2:
        hi_s = lo_s + step * 2
    return round(lo_s, 10), round(hi_s, 10)


def step_decimals(step):
    for d in range(0, 6):
        if abs(round(step, d) - step) < 1e-9 * max(1.0, abs(step)):
            return d
    return 5


def fmt_num(v, step):
    d = step_decimals(step)
    if abs(v) < step * 1e-6:
        v = 0.0
    s = ("%." + str(d) + "f") % v
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def resolve_range(data_lo, data_hi, user_range, target_div=9.0):
    """返回 (lo, hi, step, divisions)，范围已吸附到刻度整数倍。"""
    if user_range:
        lo, hi = user_range
        if hi <= lo:
            raise SystemExit("[error] 范围上限必须大于下限")
        step = pick_step(hi - lo, target_div)
        lo, hi = snap(lo, hi, step)
        return lo, hi, step, int(round((hi - lo) / step))

    span = data_hi - data_lo
    if span <= 0:
        span = abs(data_lo) * 0.2 or 1.0
    pad = span * 0.06
    lo, hi = data_lo - pad, data_hi + pad
    step = pick_step(hi - lo, target_div)
    lo, hi = snap(lo, hi, step)
    div = int(round((hi - lo) / step))
    if div > 12:  # 吸附后可能多出一格
        step = pick_step(div * step, target_div + 1)
        lo, hi = snap(lo, hi, step)
        div = int(round((hi - lo) / step))
    return lo, hi, step, div


# ----------------------------------------------------------------------------
# 网格
# ----------------------------------------------------------------------------
def draw_mm_grid(ax, xlo, xhi, ylo, yhi, sx, sy, grid_mm):
    """画 1mm / 5mm / 10mm 三级网格，全部从原点起算。"""
    if grid_mm == "none":
        return

    def lines(lo, hi, step):
        n = int(round((hi - lo) / step))
        major = [lo + i * step for i in range(n + 1)]
        mid, minor = [], []
        for i in range(n):
            for j in range(1, 10):
                v = lo + i * step + j * step / 10.0
                if abs(v - lo) < 1e-9 or abs(v - hi) < 1e-9:
                    continue
                (mid if j == 5 else minor).append(v)
        return major, mid, minor

    xmaj, xmid, xmin = lines(xlo, xhi, sx)
    ymaj, ymid, ymin = lines(ylo, yhi, sy)

    if grid_mm == "mm":
        ax.vlines(xmin, ylo, yhi, zorder=0, **GRID_MINOR)
        ax.hlines(ymin, xlo, xhi, zorder=0, **GRID_MINOR)
        ax.vlines(xmid, ylo, yhi, zorder=0, **GRID_MID)
        ax.hlines(ymid, xlo, xhi, zorder=0, **GRID_MID)

    ax.vlines(xmaj, ylo, yhi, zorder=1, **GRID_MAJOR)
    ax.hlines(ymaj, xlo, xhi, zorder=1, **GRID_MAJOR)


# ----------------------------------------------------------------------------
# 连线
# ----------------------------------------------------------------------------
def _dedup(x, y):
    """合并重复 x（取平均），平滑曲线要求 x 严格递增。"""
    xu, inv = np.unique(x, return_inverse=True)
    if len(xu) == len(x):
        return x, y
    yu = np.zeros_like(xu)
    cnt = np.zeros_like(xu)
    np.add.at(yu, inv, y)
    np.add.at(cnt, inv, 1)
    return xu, yu / cnt


def smooth_curve(x, y, n=400):
    """平滑曲线：x 单调用三次样条，非单调（滞回环）用参数样条。"""
    if len(x) < 3:
        return x, y
    monotonic = np.all(np.diff(x) > 0)
    try:
        from scipy.interpolate import make_interp_spline, splprep, splev
        if monotonic:
            xx, yy = _dedup(x, y)
            k = min(3, len(xx) - 1)
            xx_s = np.linspace(xx[0], xx[-1], n)
            return xx_s, make_interp_spline(xx, yy, k=k)(xx_s)
        tck, _ = splprep([x, y], s=0, k=min(3, len(x) - 1))
        u = np.linspace(0, 1, n)
        xs, ys = splev(u, tck)
        return np.asarray(xs), np.asarray(ys)
    except Exception:
        # 无 scipy 时的兜底：分段 Catmull-Rom（参数化），不会出现龙格振荡
        p = np.column_stack([x, y])
        if len(p) < 4:
            return x, y
        out = []
        for i in range(len(p) - 1):
            p0 = p[max(i - 1, 0)]
            p1, p2 = p[i], p[i + 1]
            p3 = p[min(i + 2, len(p) - 1)]
            t = np.linspace(0, 1, max(2, n // (len(p) - 1)), endpoint=False)[:, None]
            pt = 0.5 * ((2 * p1) + (-p0 + p2) * t
                        + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                        + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append(pt)
        out.append(p[-1][None, :])
        pts = np.vstack(out)
        return pts[:, 0], pts[:, 1]


def linear_fit(x, y, span="axis", xlo=None, xhi=None):
    k, b = np.polyfit(x, y, 1)
    if span == "axis" and xlo is not None:
        xx = np.array([xlo, xhi], dtype=float)
    else:
        xx = np.array([x.min(), x.max()], dtype=float)
    yy = k * xx + b
    yhat = k * x + b
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return xx, yy, k, b, r2


# ----------------------------------------------------------------------------
# 单面板
# ----------------------------------------------------------------------------
def draw_panel(ax, panel, cfg, xlo, xhi, ylo, yhi, sx, sy):
    colored = cfg.color == "color"

    draw_mm_grid(ax, xlo, xhi, ylo, yhi, sx, sy, cfg.grid)

    ax.set_xlim(xlo, xhi)
    ax.set_ylim(ylo, yhi)

    n_div_x = int(round((xhi - xlo) / sx))
    n_div_y = int(round((yhi - ylo) / sy))
    ax.set_xticks([round(xlo + i * sx, 10) for i in range(n_div_x + 1)])
    ax.set_yticks([round(ylo + i * sy, 10) for i in range(n_div_y + 1)])
    ax.set_xticklabels([fmt_num(xlo + i * sx, sx) for i in range(n_div_x + 1)])
    ax.set_yticklabels([fmt_num(ylo + i * sy, sy) for i in range(n_div_y + 1)])
    # 5mm 处的短刻度线（不标数字）
    ax.set_xticks([xlo + (i + 0.5) * sx for i in range(n_div_x)], minor=True)
    ax.set_yticks([ylo + (i + 0.5) * sy for i in range(n_div_y)], minor=True)

    ax.tick_params(axis="both", which="major", direction="out", length=3.2,
                   width=0.9, labelsize=cfg.tick_font, colors=INK, pad=2.5)
    ax.tick_params(axis="both", which="minor", direction="out", length=1.8,
                   width=0.6, colors=INK)
    for spine in ax.spines.values():
        spine.set_linewidth(1.1)
        spine.set_color(INK)
    ax.set_axisbelow(True)

    if panel.get("xlabel") is not None:
        ax.set_xlabel(panel["xlabel"], fontsize=cfg.label_font, color=INK, labelpad=4)
    if panel.get("ylabel") is not None:
        ax.set_ylabel(panel["ylabel"], fontsize=cfg.label_font, color=INK, labelpad=4)
    if panel.get("title"):
        ax.set_title(panel["title"], loc="left", fontsize=cfg.title_font,
                     color=INK, pad=5)

    # ---- 数据 ----
    for si, series in enumerate(panel["series"]):
        c = COLORS[si % len(COLORS)] if colored else INK
        mk = MARKERS[si % len(MARKERS)]
        x, y = series["x"], series["y"]
        label = series.get("label") or "数据%d" % (si + 1)

        ax.plot(x, y, linestyle="none", marker=mk, markersize=5.0,
                markerfacecolor="white", markeredgecolor=c, markeredgewidth=1.0,
                zorder=5, label=label)

        if panel["mode"] == "line":
            ax.plot(x, y, "-", color=c, lw=1.4, zorder=4, solid_capstyle="round")
        elif panel["mode"] == "smooth":
            xs, ys = smooth_curve(x, y)
            ax.plot(xs, ys, "-", color=c, lw=1.4, zorder=4, solid_capstyle="round")
        elif panel["mode"] == "fit" and len(x) >= 2:
            fxx, fyy, k, b, r2 = linear_fit(x, y, panel["fit_span"], xlo, xhi)
            ax.plot(fxx, fyy, "-", color=c, lw=1.4, zorder=4, solid_capstyle="round")
            if si == 0:
                txt = "y = %s x %s %s\nR² = %.4f" % (
                    _num(k), "+" if b >= 0 else "−", _num(abs(b)), r2)
                ax.text(0.035, 0.965, txt, transform=ax.transAxes,
                        fontsize=cfg.note_font, color=INK, va="top", ha="left",
                        family=rcParams["font.sans-serif"][0],
                        bbox=dict(boxstyle="round,pad=0.28", facecolor="white",
                                  edgecolor="#9a9a9a", linewidth=0.6),
                        zorder=6)

    if panel.get("legend") and len(panel["series"]) > 1:
        lg = ax.legend(loc="best", fontsize=cfg.legend_font, frameon=True,
                       handlelength=1.6, borderpad=0.35, labelspacing=0.3)
        lg.get_frame().set_edgecolor("#9a9a9a")
        lg.get_frame().set_linewidth(0.6)


def _num(v):
    if v == 0:
        return "0"
    a = abs(v)
    if a >= 1000 or a < 0.01:
        return ("%.3e" % v).replace("e+", "×10^").replace("e-", "×10^-")
    if a >= 100:
        return "%.2f" % v
    if a >= 1:
        return "%.3f" % v
    return "%.4f" % v


# ----------------------------------------------------------------------------
# 参数
# ----------------------------------------------------------------------------
def parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="plot.py",
        description="毫米坐标纸风格曲线图（供打印后手绘抄图）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python plot.py --csv examples/demo_spring.csv --x m --y x "
               "--xlabel \"质量 m / g\" --ylabel \"伸长量 x / mm\" --mode fit\n")
    p.add_argument("--csv", required=True, help="第一张子图的数据文件（CSV）")
    p.add_argument("--x", default="0", help="x 列名或列序号（默认第 0 列）")
    p.add_argument("--y", nargs="+", default=None, help="y 列名，可多个（空格或逗号分隔）")
    p.add_argument("--labels", default=None, help="图例文字，逗号分隔，与 --y 对应")
    p.add_argument("--xlabel", default=None, help="x 轴标签，可含单位，如 \"位置 x / mm\"")
    p.add_argument("--ylabel", default=None, help="y 轴标签")
    p.add_argument("--title", default=None, help="整张图标题")
    p.add_argument("--panel-title", default=None, help="第一张子图左上角小标题")

    p.add_argument("--mode", default="line",
                   choices=["line", "smooth", "fit", "scatter"],
                   help="连线方式：折线/平滑/线性拟合/只画点（默认 line）")
    p.add_argument("--fit-span", default="axis", choices=["axis", "data"],
                   help="拟合线画满整幅坐标还是只覆盖数据段")

    p.add_argument("--panel2-csv", default=None, help="第二张子图的数据文件；给了就画上下两个子图")
    p.add_argument("--panel2-x", default="0", help="第二张子图的 x 列")
    p.add_argument("--panel2-y", nargs="+", default=None, help="第二张子图的 y 列")
    p.add_argument("--panel2-labels", default=None, help="第二张子图的图例文字")
    p.add_argument("--panel2-xlabel", default=None)
    p.add_argument("--panel2-ylabel", default=None)
    p.add_argument("--panel2-title", default=None)
    p.add_argument("--panel2-mode", default=None,
                   choices=["line", "smooth", "fit", "scatter"],
                   help="第二张子图的连线方式，默认与 --mode 相同")

    p.add_argument("--xlim", default=None, help="x 范围，如 0,60（不给就自动）")
    p.add_argument("--ylim", default=None, help="y 范围，如 0,5")
    p.add_argument("--panel2-xlim", default=None)
    p.add_argument("--panel2-ylim", default=None)
    p.add_argument("--xtick", type=float, default=None, help="x 轴大格间隔（数据单位），不给就自动")
    p.add_argument("--ytick", type=float, default=None, help="y 轴大格间隔")
    p.add_argument("--panel2-xtick", type=float, default=None)
    p.add_argument("--panel2-ytick", type=float, default=None)

    p.add_argument("--grid", default="mm", choices=["mm", "normal", "none"],
                   help="mm=1/5/10mm 三级网格（默认）；normal=只画大格；none=不画网格")
    p.add_argument("--color", default="black", choices=["black", "color"],
                   help="black=纯黑白打印友好（默认）；color=彩色系列")
    p.add_argument("--dpi", type=int, default=300, help="输出分辨率（默认 300）")
    p.add_argument("--out", default=None, help="输出 PNG 路径，默认与 CSV 同目录的 <csv名>.png")
    p.add_argument("--font", default=None, help="强制指定字体名，如 SimHei")
    p.add_argument("--no-header", action="store_true", help="CSV 没有表头行")
    p.add_argument("--delimiter", default="auto", help="分隔符，默认自动识别")
    p.add_argument("--no-legend", action="store_true", help="不画图例")

    p.add_argument("--label-font", type=float, default=12.5)
    p.add_argument("--tick-font", type=float, default=10.5)
    p.add_argument("--note-font", type=float, default=10.0)
    p.add_argument("--legend-font", type=float, default=10.0)
    return p.parse_args(argv)


def split_cols(v):
    if v is None:
        return []
    items = [v] if isinstance(v, str) else list(v)
    out = []
    for item in items:
        out.extend([s for s in str(item).replace("，", ",").split(",") if s.strip()])
    return out


def parse_range(s):
    if not s:
        return None
    parts = [p for p in str(s).replace("，", ",").split(",") if p.strip()]
    if len(parts) != 2:
        raise SystemExit("[error] 范围要写成 \"下限,上限\"，例如 --ylim 0,5")
    return float(parts[0]), float(parts[1])


def default_out(csv_path):
    base = os.path.splitext(os.path.basename(csv_path))[0]
    return os.path.join(os.path.dirname(os.path.abspath(csv_path)), base + ".png")


# ----------------------------------------------------------------------------
def main(argv=None):
    cfg = parse_args(argv)
    font = setup_font(cfg.font)
    print("[info] 中文字体: %s" % font)

    cfg.title_font = max(12.0, cfg.label_font + 0.5)

    panels = []

    # ---- 面板 1 ----
    ycols = split_cols(cfg.y) or ["1"]
    x1, ys1, names1, _, _ = read_csv(
        cfg.csv, cfg.x, ycols, None if not cfg.no_header else False, cfg.delimiter)
    labels1 = split_cols(cfg.labels)
    panels.append(dict(
        x=x1,
        series=[dict(x=x1, y=y, label=(labels1[i] if i < len(labels1) else names1[i + 1]))
                for i, y in enumerate(ys1)],
        mode=cfg.mode, fit_span=cfg.fit_span,
        xlabel=cfg.xlabel or names1[0],
        ylabel=cfg.ylabel or (names1[1] if len(names1) > 1 else "y"),
        title=cfg.panel_title,
        legend=(not cfg.no_legend) and len(ys1) > 1,
    ))

    # ---- 面板 2 ----
    if cfg.panel2_csv:
        ycols2 = split_cols(cfg.panel2_y) or ["1"]
        x2, ys2, names2, _, _ = read_csv(
            cfg.panel2_csv, cfg.panel2_x, ycols2,
            None if not cfg.no_header else False, cfg.delimiter)
        labels2 = split_cols(cfg.panel2_labels)
        panels.append(dict(
            x=x2,
            series=[dict(x=x2, y=y, label=(labels2[i] if i < len(labels2) else names2[i + 1]))
                    for i, y in enumerate(ys2)],
            mode=cfg.panel2_mode or cfg.mode, fit_span=cfg.fit_span,
            xlabel=cfg.panel2_xlabel or names2[0],
            ylabel=cfg.panel2_ylabel or (names2[1] if len(names2) > 1 else "y"),
            title=cfg.panel2_title,
            legend=(not cfg.no_legend) and len(ys2) > 1,
        ))

    # ---- 范围 ----
    for i, pnl in enumerate(panels):
        ys_all = np.concatenate([s["y"] for s in pnl["series"]])
        if i == 0:
            ur = parse_range(cfg.xlim), parse_range(cfg.ylim)
            us = cfg.xtick, cfg.ytick
        else:
            ur = parse_range(cfg.panel2_xlim), parse_range(cfg.panel2_ylim)
            us = cfg.panel2_xtick, cfg.panel2_ytick

        xlo, xhi, sx, dx = resolve_range(float(np.min(pnl["x"])), float(np.max(pnl["x"])), ur[0])
        ylo, yhi, sy, dy = resolve_range(float(ys_all.min()), float(ys_all.max()), ur[1])
        if us[0]:
            sx = float(us[0]); xlo, xhi = snap(xlo, xhi, sx); dx = int(round((xhi - xlo) / sx))
        if us[1]:
            sy = float(us[1]); ylo, yhi = snap(ylo, yhi, sy); dy = int(round((yhi - ylo) / sy))
        pnl.update(xlo=xlo, xhi=xhi, ylo=ylo, yhi=yhi, sx=sx, sy=sy, dx=dx, dy=dy)

    # 两个子图必须等宽：格子数取大者，另一个把空余补到坐标范围高端
    if len(panels) == 2:
        dmax = max(p["dx"] for p in panels)
        for pnl in panels:
            extra = dmax - pnl["dx"]
            if extra > 0:
                pnl["xhi"] = round(pnl["xhi"] + extra * pnl["sx"], 10)
                pnl["dx"] = dmax
                print("[info] 为了让上下两图等宽，x 轴上限扩到 %s"
                      % fmt_num(pnl["xhi"], pnl["sx"]))

    # ---- 物理尺寸：大格 = 10mm，小格才是 1mm ----
    grid_mm = 10.0
    ax_w_mm = max(p["dx"] for p in panels) * grid_mm
    heights = [p["dy"] * grid_mm for p in panels]

    left_mm = 25.0
    right_mm = 11.0
    bottom_mm = 21.0
    panel_title_mm = 8.0 if any(p["title"] for p in panels) else 3.0
    fig_title_mm = 11.0 if cfg.title else 0.0
    gap_mm = 22.0 if len(panels) == 2 else 0.0

    fig_w_mm = left_mm + ax_w_mm + right_mm
    fig_h_mm = bottom_mm + sum(heights) + gap_mm + panel_title_mm + fig_title_mm

    fig = plt.figure(figsize=(fig_w_mm * MM, fig_h_mm * MM), dpi=cfg.dpi,
                     facecolor="white")

    y_cursor = bottom_mm
    rects = []
    for pnl, h in reversed(list(zip(panels, heights))):  # 第二个子图在下面
        rects.append((left_mm, y_cursor, ax_w_mm, h))
        y_cursor += h + gap_mm
    rects.reverse()

    for pnl, (rx, ry, rw, rh) in zip(panels, rects):
        ax = fig.add_axes([rx / fig_w_mm, ry / fig_h_mm,
                           rw / fig_w_mm, rh / fig_h_mm])
        draw_panel(ax, pnl, cfg, pnl["xlo"], pnl["xhi"], pnl["ylo"], pnl["yhi"],
                   pnl["sx"], pnl["sy"])

    if cfg.title:
        fig.text(0.012, 1 - 4.0 / fig_h_mm, cfg.title, ha="left", va="top",
                 fontsize=cfg.title_font + 1.5, color=INK)

    out = cfg.out or default_out(cfg.csv)
    out = os.path.abspath(out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=cfg.dpi, facecolor="white")  # 不能用 bbox_inches='tight'
    plt.close(fig)

    print("[ok] 已输出 %s" % out)
    print("[info] 版心 %.1f x %.1f mm，x 轴 %d 大格 / y 轴 %s，图片 %d x %d px"
          % (ax_w_mm, sum(heights), panels[0]["dx"],
             "/".join(str(p["dy"]) for p in panels),
             round(fig_w_mm * MM * cfg.dpi), round(fig_h_mm * MM * cfg.dpi)))
    if ax_w_mm < 70 or min(heights) < 60:
        print("[warn] 版心偏小（%.0f x %.0f mm），刻度和字会比较挤；"
              "把 --xtick/--ytick 改小一点可以多给几格。"
              % (ax_w_mm, min(heights)), file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
