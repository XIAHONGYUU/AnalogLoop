#!/usr/bin/env python3
"""Generate the AnalogLoop diagrams.

All figures are authored from scratch with primitives in this file. No source
image from the design discussion is copied or embedded.

Outputs:
  diagrams/architecture.svg
  diagrams/fast-verification.svg
  diagrams/mcu-mapping.svg
  diagrams/png/*.png  (if cairosvg is available)
"""
from __future__ import annotations

import html
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "diagrams"
PNG = OUT / "png"

FONT = "'Noto Sans CJK SC','Source Han Sans SC','WenQuanYi Zen Hei',sans-serif"
MONO = "'Noto Sans Mono CJK SC','DejaVu Sans Mono',monospace"

INK = "#1f2937"
MUTED = "#5b6778"
FAINT = "#8a94a6"
BG = "#f7f9fc"
WHITE = "#ffffff"
GREEN = "#2f8f6b"
GREEN_BG = "#e8f5ef"
BLUE = "#2b6cb0"
BLUE_BG = "#e8f1fb"
AMBER = "#a86a12"
AMBER_BG = "#fff6e5"
PURPLE = "#6b46c1"
PURPLE_BG = "#f1ebff"
TEAL = "#2c7a7b"
TEAL_BG = "#e6f4f4"
ORANGE = "#c05621"
ORANGE_BG = "#feebc8"
RED = "#c53030"
RED_BG = "#fff5f5"
GRAY_BG = "#eef1f5"


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def text(x, y, s, size=16, fill=INK, weight=400, anchor="start", font=FONT, opacity=1.0, ls=None):
    extra = f' letter-spacing="{ls}"' if ls else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
        f'opacity="{opacity}"{extra}>{esc(s)}</text>'
    )


def lines(x, y, items, size=15.5, lh=27, fill=INK, weight=400, anchor="start", bullet=False):
    out = []
    for i, item in enumerate(items):
        s = ("· " + item) if bullet else item
        out.append(text(x, y + i * lh, s, size=size, fill=fill, weight=weight, anchor=anchor))
    return "".join(out)


def rect(x, y, w, h, fill=WHITE, stroke="none", sw=1.4, rx=14, dash=None, opacity=1.0):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'opacity="{opacity}"{dash_attr}/>'
    )


def circle(cx, cy, r, fill, stroke="none", sw=1.4):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def badge(cx, cy, n, color, bg=WHITE, r=15):
    return circle(cx, cy, r, bg, color, 1.6) + text(cx, cy + 5.5, str(n), 15, color, 700, "middle")


def arrow(x1, y1, x2, y2, color, sw=2.2, dash=None, head=10):
    ang = math.atan2(y2 - y1, x2 - x1)
    # stop the shaft just short of the head so the joint looks clean
    bx = x2 - math.cos(ang) * head * 0.85
    by = y2 - math.sin(ang) * head * 0.85
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    shaft = (
        f'<line x1="{x1}" y1="{y1}" x2="{bx:.2f}" y2="{by:.2f}" '
        f'stroke="{color}" stroke-width="{sw}" stroke-linecap="round"{dash_attr}/>'
    )
    a1 = ang + 0.42
    a2 = ang - 0.42
    p1 = (x2, y2)
    p2 = (x2 - head * math.cos(a1), y2 - head * math.sin(a1))
    p3 = (x2 - head * math.cos(a2), y2 - head * math.sin(a2))
    head_svg = (
        f'<polygon points="{p1[0]:.2f},{p1[1]:.2f} {p2[0]:.2f},{p2[1]:.2f} '
        f'{p3[0]:.2f},{p3[1]:.2f}" fill="{color}"/>'
    )
    return shaft + head_svg


def poly(points, color, sw=2.2, dash=None, fill="none"):
    d = "M " + " L ".join(f"{x},{y}" for x, y in points)
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="{fill}" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>'


def pill(cx, cy, s, size=14, fill=MUTED, bg=BG, pad=8):
    width = estimate_width(s, size) + pad * 2
    height = size + 10
    return (
        rect(cx - width / 2, cy - height / 2, width, height, bg, "none", 0, height / 2)
        + text(cx, cy + size * 0.36, s, size, fill, 500, "middle")
    )


def estimate_width(s, size):
    total = 0.0
    for ch in str(s):
        total += size if ord(ch) > 127 else size * 0.56
    return total


def svg_open(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" role="img">'
        f'<rect width="{w}" height="{h}" fill="{BG}"/>'
    )


def footer(w, h, note="v0.1 · 2026-10 · 设计构想，非流片验证"):
    return (
        f'<line x1="50" y1="{h-34}" x2="{w-50}" y2="{h-34}" stroke="#dde3ea" stroke-width="1"/>'
        + text(50, h - 14, "AnalogLoop · architecture note", 12.5, FAINT)
        + text(w - 50, h - 14, note, 12.5, FAINT, anchor="end")
    )


def header(w, title, subtitle, legend=None):
    s = text(60, 64, title, 38, INK, 700)
    s += text(60, 104, subtitle, 18.5, MUTED)
    if legend:
        x = 60
        y = 140
        for color, label, dash in legend:
            s += f'<line x1="{x}" y1="{y-5}" x2="{x+34}" y2="{y-5}" stroke="{color}" stroke-width="2.4"'
            if dash:
                s += f' stroke-dasharray="{dash}"'
            s += "/>"
            s += text(x + 42, y, label, 13.5, MUTED)
            x += 42 + estimate_width(label, 13.5) + 34
    return s


def block(x, y, w, h, n, title, color, bg, bullets, body_size=15.2, lh=27):
    s = rect(x, y, w, h, bg, color, 1.5)
    s += rect(x, y, w, 56, bg, "none", 0, 14)
    s += badge(x + 28, y + 30, n, color, WHITE, 15)
    s += text(x + 52, y + 37, title, 20.5, color, 700)
    s += lines(x + 22, y + 88, bullets, size=body_size, lh=lh, bullet=True)
    return s


def architecture():
    W, H = 1680, 790
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "AnalogLoop：两层验证的模拟设计闭环",
        "策略层发意图 · 执行层确定性执行 · 代理模型快筛 · 真实 SPICE 签核",
        legend=[
            (GREEN, "数据 / 控制", None),
            (BLUE, "反馈", "7 6"),
            (ORANGE, "快路径", None),
            (RED, "真值", None),
        ],
    ))

    y, h = 180, 340

    s.append(block(50, y, 240, h, 1, "目标与约束", GREEN, GREEN_BG, [
        "设计目标",
        "Gain / UGB / PM",
        "约束：功耗 · 面积",
        "参数范围与步进",
        "PVT 角落",
        "可行性预检",
    ]))

    s.append(block(340, y, 270, h, 2, "策略层（LLM）", BLUE, BLUE_BG, [
        "理解目标与约束",
        "选择搜索策略",
        "按角色诊断失败",
        "决定何时停",
        "不做数值计算",
        "不持有数值状态",
    ]))

    s.append(block(660, y, 300, h, 3, "工具链（确定性）", AMBER, AMBER_BG, [
        "解析角色 / 网表",
        "渲染 Deck / 测试台",
        "DoE · BO · 局部搜索",
        "调用快速代理",
        "测量 · 面积估计",
        "写 case 账本",
    ], body_size=14.6))

    # Verification block (4) with two speeds and a promotion gate.
    bx, bw = 1010, 370
    s.append(rect(bx, y, bw, h, PURPLE_BG, PURPLE, 1.5))
    s.append(badge(bx + 28, y + 30, 4, PURPLE, WHITE, 15))
    s.append(text(bx + 52, y + 37, "验证层：两种速度", 20.5, PURPLE, 700))

    ax, aw = bx + 18, bw - 36
    # 4a
    s.append(rect(ax, y + 52, aw, 82, WHITE, ORANGE, 1.3, 10))
    s.append(text(ax + 16, y + 78, "4a  快速代理", 16.5, ORANGE, 700))
    s.append(text(ax + 16, y + 102, "gm/ID 表 · 器件 NN · 电路 GP", 14.2, INK))
    s.append(text(ax + 16, y + 123, "毫秒级，带 μ / σ 与 OOD", 14.2, MUTED))
    # gate
    gy = y + 146
    s.append(rect(ax + 22, gy, aw - 44, 46, ORANGE_BG, ORANGE, 1.3, 10))
    s.append(text(ax + aw / 2, gy + 29, "晋级门：误差 × 裕量 × 置信度", 14.2, ORANGE, 600, "middle"))
    # 4b
    by = y + 208
    s.append(rect(ax, by, aw, 82, WHITE, RED, 1.3, 10))
    s.append(text(ax + 16, by + 26, "4b  真实 SPICE", 16.5, RED, 700))
    s.append(text(ax + 16, by + 50, "ngspice · HSPICE · Spectre", 14.2, INK))
    s.append(text(ax + 16, by + 71, "秒–分钟，签核真值", 14.2, MUTED))
    # inside arrows
    s.append(arrow(bx + bw / 2, y + 134, bx + bw / 2, gy - 4, ORANGE, 2.0, None, 8))
    s.append(arrow(bx + bw / 2, gy + 46, bx + bw / 2, by - 4, RED, 2.0, "5 4", 8))
    s.append(text(bx + bw / 2 + 12, gy + 78, "边界 / 不确定 / 签核", 12.8, RED))

    s.append(block(1430, y, 200, h, 5, "记忆与知识", TEAL, TEAL_BG, [
        "Case 账本",
        "技能 / 规则",
        "代理模型",
        "负知识",
        "可重放",
    ], body_size=14.8))

    # main data arrows
    s.append(arrow(290, y + 170, 338, y + 170, GREEN))
    s.append(arrow(610, y + 170, 658, y + 170, BLUE))
    s.append(arrow(960, y + 170, 1008, y + 170, AMBER))
    s.append(arrow(1380, y + 170, 1428, y + 170, PURPLE))

    # feedback loops
    # memory -> policy (inner loop)
    s.append(poly([(1530, y + h), (1530, 535), (475, 535), (475, y + h + 2)], BLUE, 2.2, "7 6"))
    s.append(arrow(475, 545, 475, y + h + 2, BLUE, 2.2, None, 9))
    s.append(pill(840, 535, "内环：性能结果 + 记忆", 13.5, BLUE))
    # memory -> goals (outer loop)
    s.append(poly([(1545, y + h), (1545, 568), (170, 568), (170, y + h + 2)], TEAL, 2.2))
    s.append(arrow(170, 578, 170, y + h + 2, TEAL, 2.2, None, 9))
    s.append(pill(1000, 568, "外环：用历史修正目标与约束", 13.5, TEAL))
    s.append(circle(1530, y + h + 15, 3.5, BLUE))

    # budget controller band
    band_y, band_h = 615, 118
    s.append(rect(50, band_y, 1580, band_h, GRAY_BG, "#cfd8e3", 1.3, 16))
    s.append(badge(80, band_y + 34, 6, MUTED, WHITE, 15))
    s.append(text(104, band_y + 41, "预算与晋级控制器", 20.5, INK, 700))
    s.append(text(104, band_y + 70, "横切 ②③④：决定快 / 慢路径、每条 case 的预算、以及何时停", 14.0, MUTED))

    cards = [
        ("仿真预算", "总量 · 剩余 / case"),
        ("快慢比", "代理 : SPICE"),
        ("晋级阈值", "kσ · 裕量 · OOD"),
        ("停机条件", "收敛 · 预算 · 可行"),
    ]
    cx0, cw, gap = 650, 220, 20
    for i, (title, sub) in enumerate(cards):
        cx = cx0 + i * (cw + gap)
        s.append(rect(cx, band_y + 22, cw, 74, WHITE, "#d5dde7", 1.1, 10))
        s.append(text(cx + 14, band_y + 48, title, 14.5, INK, 700))
        s.append(text(cx + 14, band_y + 72, sub, 12.8, MUTED))
    s.append(text(60, band_y + band_h - 12, "控制信号不进入 LLM 上下文：只以工具参数与停机条件出现。", 12.5, FAINT))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)


def fast_verification():
    W, H = 1600, 980
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "快速验证：95% 是预算，不是承诺",
        "代理模型负责探索，真实 SPICE 负责签核；晋级门决定谁走哪条路。",
    ))

    # left flow
    x, w = 70, 330
    s.append(rect(x, 150, w, 78, ORANGE_BG, ORANGE, 1.4, 12))
    s.append(text(x + 16, 179, "候选设计 x", 17, ORANGE, 700))
    s.append(text(x + 16, 204, "W/L · 偏置 · 角落 · 温度", 13.8, MUTED))

    s.append(rect(x, 262, w, 88, WHITE, ORANGE, 1.2, 12))
    s.append(text(x + 16, 290, "特征 / 中间表示", 16.5, INK, 700))
    s.append(text(x + 16, 315, "gm/ID · fT · gm/gds · Vov", 13.8, MUTED))
    s.append(text(x + 16, 337, "把 PDK 差异压到可移植特征", 13.0, FAINT))

    s.append(rect(x, 384, w, 96, WHITE, ORANGE, 1.2, 12))
    s.append(text(x + 16, 412, "快速预测器", 16.5, INK, 700))
    s.append(text(x + 16, 437, "μ, σ, OOD score", 13.8, MUTED))
    s.append(text(x + 16, 459, "表模型 / GP / NN", 13.0, FAINT))

    # gate diamond
    gx, gy, gw, gh = 235, 520, 170, 96
    s.append(f'<polygon points="{gx},{gy+gh/2} {gx+gw/2},{gy} {gx+gw},{gy+gh/2} {gx+gw/2},{gy+gh}" fill="{ORANGE_BG}" stroke="{ORANGE}" stroke-width="1.5"/>')
    s.append(text(gx + gw / 2, gy + 42, "晋级门", 16.5, ORANGE, 700, "middle"))
    s.append(text(gx + gw / 2, gy + 64, "kσ < 裕量 ?", 13.0, INK, 400, "middle"))

    s.append(arrow(x + w / 2, 228, x + w / 2, 258, ORANGE))
    s.append(arrow(x + w / 2, 350, x + w / 2, 380, ORANGE))
    s.append(arrow(x + w / 2, 480, x + w / 2, gy - 2, ORANGE))

    # accept path
    s.append(rect(430, 520, 250, 78, GREEN_BG, GREEN, 1.4, 12))
    s.append(text(446, 549, "接受（快路径）", 16.5, GREEN, 700))
    s.append(text(446, 574, "写账本，标记 proxy", 13.5, MUTED))
    s.append(arrow(gx + gw, gy + gh / 2, 426, gy + gh / 2, GREEN))
    s.append(text(405, gy + 60, "是", 13, GREEN, 600))

    # reject path
    s.append(rect(x, 700, w, 88, RED_BG, RED, 1.4, 12))
    s.append(text(x + 16, 729, "真实 SPICE", 16.5, RED, 700))
    s.append(text(x + 16, 754, "签核 / 边界 / 抽样复核", 13.5, MUTED))
    s.append(arrow(gx + gw / 2, gy + gh, gx + gw / 2, 696, RED))
    s.append(text(gx + gw / 2 + 12, gy + gh + 28, "否 / 不确定", 12.8, RED))

    s.append(rect(430, 700, 250, 88, WHITE, RED, 1.2, 12))
    s.append(text(446, 729, "更新误差模型", 16.5, RED, 700))
    s.append(text(446, 754, "trust region · 校准", 13.5, MUTED))
    s.append(arrow(400, 744, 426, 744, RED))

    # calibration back to predictor
    s.append(poly([(680, 744), (770, 744), (770, 432), (404, 432)], RED, 1.8, "6 5"))
    s.append(arrow(770, 432, 404, 432, RED, 1.8, None, 8))
    s.append(pill(770, 560, "周期校准", 12.5, RED))

    # right panel
    px, py, pw, ph = 850, 150, 690, 560
    s.append(rect(px, py, pw, ph, WHITE, "#d5dde7", 1.2, 16))
    s.append(text(px + 28, py + 40, "95% 的四种定义", 23, INK, 700))
    s.append(text(px + 28, py + 66, "把口号拆成可测指标，否则无法验收", 13.5, MUTED))

    defs = [
        ("精度", "逐指标 |Δ| ≤ 5%，不是全局平均"),
        ("工作量", "95% 候选走快路径，5% 进 SPICE"),
        ("安全", "误接受率 ≤ 0.5%，比平均误差更重要"),
        ("覆盖", "95% 的角落 / 工况落在信任域内"),
    ]
    for i, (title, sub) in enumerate(defs):
        cy = py + 94 + i * 78
        s.append(rect(px + 24, cy, pw - 48, 64, BG, "#e1e7ee", 1.0, 10))
        s.append(text(px + 40, cy + 26, f"{i+1}. {title}", 15.5, ORANGE, 700))
        s.append(text(px + 40, cy + 48, sub, 13.3, INK))

    # tolerance table
    tx, ty = px + 24, py + 430
    s.append(text(tx, ty, "指标容差（示例，需按电路标定）", 14.5, INK, 700))
    rows = [
        ("Gain", "1.0 dB", "UGB", "5%"),
        ("PM", "3°", "Power", "5%"),
        ("Noise", "10%", "Offset", "15%"),
    ]
    for i, (a, b, c, d) in enumerate(rows):
        ry = ty + 28 + i * 26
        s.append(text(tx, ry, a, 13.2, MUTED))
        s.append(text(tx + 90, ry, b, 13.2, INK, 600))
        s.append(text(tx + 220, ry, c, 13.2, MUTED))
        s.append(text(tx + 310, ry, d, 13.2, INK, 600))
    s.append(text(tx, ty + 116, "PM / 启动 / 失真靠近边界时非线性，必须 SPICE + 裕量。", 12.3, RED))

    # cost band
    by = 792
    s.append(rect(70, by, 1460, 130, WHITE, "#d5dde7", 1.2, 16))
    s.append(text(96, by + 38, "成本模型", 18.5, INK, 700))
    s.append(text(96, by + 68, "1 次代理评估", 13.5, MUTED))
    s.append(text(96, by + 94, "≈ 1 ms – 1 s", 19, ORANGE, 700))
    s.append(text(360, by + 68, "1 次 SPICE", 13.5, MUTED))
    s.append(text(360, by + 94, "≈ 1 s – 10 min", 19, RED, 700))
    s.append(text(640, by + 68, "目标快路径占比", 13.5, MUTED))
    s.append(text(640, by + 94, "80% – 95%", 19, GREEN, 700))
    s.append(text(900, by + 68, "安全红线", 13.5, MUTED))
    s.append(text(900, by + 94, "误接受 ≤ 0.5%", 19, RED, 700))
    s.append(text(1180, by + 68, "原则", 13.5, MUTED))
    s.append(text(1180, by + 94, "宁可多问一次 SPICE", 16.5, INK, 600))

    # split bar
    s.append(rect(96, by + 108, 1400, 8, "#e9edf3", "none", 0, 4))
    s.append(rect(96, by + 108, 1400 * 0.9, 8, ORANGE, "none", 0, 4))
    s.append(rect(96 + 1400 * 0.9, by + 108, 1400 * 0.1, 8, RED, "none", 0, 4))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)


def mcu_mapping():
    W, H = 1600, 900
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "MCU 类比：分工，而不是性能",
        "CPU 调度外设；策略层调度工具链与两种速度的验证。",
    ))

    left = [
        ("策略层（LLM）", "选策略 · 诊断 · 停机", BLUE, BLUE_BG),
        ("工具链（确定性）", "Deck · DoE/BO · 测量", AMBER, AMBER_BG),
        ("快速代理", "gm/ID · 表 · GP / NN", ORANGE, ORANGE_BG),
        ("真实 SPICE", "ngspice · HSPICE", RED, RED_BG),
        ("记忆与账本", "case · 技能 · 负知识", TEAL, TEAL_BG),
    ]
    right = [
        ("CPU 内核", "调度 · 控制流", BLUE, BLUE_BG),
        ("外设 / 驱动", "定时器 · ADC · 总线", AMBER, AMBER_BG),
        ("L1 Cache", "快，近似，可能 miss", ORANGE, ORANGE_BG),
        ("DRAM", "慢，精确", RED, RED_BG),
        ("Flash / 磁盘", "持久化", TEAL, TEAL_BG),
    ]
    labels = ["策略 ≈ CPU", "工具 ≈ 外设", "代理 ≈ L1", "SPICE ≈ DRAM", "记忆 ≈ Flash"]

    for i in range(5):
        y = 170 + i * 105
        s.append(rect(70, y, 500, 82, left[i][3], left[i][2], 1.4, 12))
        s.append(text(90, y + 32, left[i][0], 17, left[i][2], 700))
        s.append(text(90, y + 57, left[i][1], 13.2, MUTED))

        s.append(rect(1030, y, 500, 82, right[i][3], right[i][2], 1.4, 12))
        s.append(text(1050, y + 32, right[i][0], 17, right[i][2], 700))
        s.append(text(1050, y + 57, right[i][1], 13.2, MUTED))

        s.append(arrow(570, y + 41, 1026, y + 41, "#9aa6b6", 1.8, "6 5", 8))
        s.append(pill(798, y + 41, labels[i], 13, MUTED, BG))

    strip_y = 700
    s.append(rect(70, strip_y, 1460, 46, GRAY_BG, "#cfd8e3", 1.1, 10))
    s.append(text(90, strip_y + 28, "ISA = 工具契约", 14, INK, 700))
    s.append(text(300, strip_y + 28, "中断 = 约束违反 / 预算耗尽 / OOD", 14, INK, 700))
    s.append(text(700, strip_y + 28, "存储层次 = 上下文 / 账本 / 技能", 14, INK, 700))

    panel_y = 770
    s.append(rect(70, panel_y, 1460, 92, WHITE, "#d5dde7", 1.2, 12))
    s.append(text(90, panel_y + 27, "类比的边界", 15, INK, 700))
    s.append(text(90, panel_y + 52, "CPU 是确定性的；LLM 是随机策略 → 需要工具契约约束", 12.8, MUTED))
    s.append(text(90, panel_y + 74, "Cache 有一致性协议；代理会误接受 → 需要晋级门与置信度", 12.8, MUTED))
    s.append(text(820, panel_y + 52, "MCU 不学习；本架构会积累", 12.8, MUTED))
    s.append(text(820, panel_y + 74, "→ 记忆是额外一层，不是 CPU 的一部分", 12.8, MUTED))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)



def pdk_fastpath():
    W, H = 1680, 940
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "从 PDK 到快速验证：两条路线，一个晋级门",
        "gm/ID 提供可移植的中间表示；学习型数据库提供速度；SPICE 提供真值。",
        legend=[
            (GREEN, "数据", None),
            (ORANGE, "快路径", None),
            (RED, "真值", None),
        ],
    ))

    # PDK
    s.append(rect(60, 160, 300, 90, GREEN_BG, GREEN, 1.4, 12))
    s.append(text(80, 193, "Open PDK", 17, GREEN, 700))
    s.append(text(80, 220, "Sky130 · GF180 · IHP SG13G2", 13.0, MUTED))

    # extraction
    s.append(rect(60, 300, 300, 110, AMBER_BG, AMBER, 1.4, 12))
    s.append(text(80, 332, "表征 / 提取", 17, AMBER, 700))
    s.append(text(80, 358, "DC 扫描 · 工作点 · C-V", 13.0, MUTED))
    s.append(text(80, 380, "每 PDK / 每角落一张表", 13.0, MUTED))
    s.append(text(80, 400, "记录版本与哈希", 12.5, FAINT))

    # route A
    s.append(rect(430, 150, 370, 140, BLUE_BG, BLUE, 1.4, 12))
    s.append(text(450, 182, "A. gm/ID 表", 18, BLUE, 700))
    s.append(text(450, 210, "gm/ID · fT · gm/gds · Id/W · Vov", 13.0, INK))
    s.append(text(450, 234, "可移植 · 可解释 · 数据小", 13.0, MUTED))
    s.append(text(450, 258, "仍需 SPICE 表征与最终验证", 12.5, FAINT))

    # route B
    s.append(rect(430, 330, 370, 150, PURPLE_BG, PURPLE, 1.4, 12))
    s.append(text(450, 362, "B. 学习型 PDK 数据库", 18, PURPLE, 700))
    s.append(text(450, 390, "器件级：I-V · C-V · 噪声 · 失配", 13.0, INK))
    s.append(text(450, 414, "电路级：performance(sizing, corner)", 13.0, INK))
    s.append(text(450, 438, "快 · 可微 · 分布外风险", 12.5, MUTED))
    s.append(text(450, 462, "需要求解器或电路级训练数据", 12.5, FAINT))

    # fast evaluator
    s.append(rect(870, 210, 300, 210, ORANGE_BG, ORANGE, 1.5, 14))
    s.append(text(892, 244, "快速评估", 18, ORANGE, 700))
    s.append(text(892, 274, "L0 查表 / L2 预测", 13.5, INK))
    s.append(text(892, 300, "输出 mu · sigma · OOD", 13.5, INK))
    s.append(text(892, 326, "毫秒 – 秒级", 13.5, MUTED))
    s.append(text(892, 356, "带版本与训练集哈希", 12.5, FAINT))
    s.append(text(892, 384, "不签核，只筛选与排序", 13.0, RED))

    # gate diamond
    gx, gy, gw, gh = 1240, 235, 180, 160
    s.append(f'<polygon points="{gx+gw/2},{gy} {gx+gw},{gy+gh/2} {gx+gw/2},{gy+gh} {gx},{gy+gh/2}" fill="{ORANGE_BG}" stroke="{ORANGE}" stroke-width="1.5"/>')
    s.append(text(gx + gw / 2, gy + 72, "晋级门", 17, ORANGE, 700, "middle"))
    s.append(text(gx + gw / 2, gy + 96, "误差 × 裕量 × OOD", 12.5, INK, 400, "middle"))

    # accept
    s.append(rect(1470, 275, 150, 80, GREEN_BG, GREEN, 1.4, 12))
    s.append(text(1490, 306, "接受", 16, GREEN, 700))
    s.append(text(1490, 330, "写账本", 12.5, MUTED))

    # SPICE
    s.append(rect(1230, 470, 390, 110, RED_BG, RED, 1.4, 12))
    s.append(text(1250, 503, "真实 SPICE", 17, RED, 700))
    s.append(text(1250, 529, "ngspice · HSPICE · Spectre", 13.2, INK))
    s.append(text(1250, 553, "签核 · 边界 · 抽样复核", 13.2, MUTED))
    s.append(text(1250, 574, "返回测量值与原始文件哈希", 12.5, FAINT))

    # arrows
    s.append(arrow(210, 250, 210, 296, GREEN))
    s.append(poly([(360, 340), (395, 340), (395, 220), (426, 220)], BLUE, 2.2))
    s.append(arrow(395, 220, 426, 220, BLUE, 2.2, None, 9))
    s.append(poly([(360, 370), (395, 370), (395, 405), (426, 405)], PURPLE, 2.2))
    s.append(arrow(395, 405, 426, 405, PURPLE, 2.2, None, 9))
    s.append(arrow(800, 220, 866, 270, BLUE, 2.0))
    s.append(arrow(800, 405, 866, 365, PURPLE, 2.0))
    s.append(arrow(1170, 315, 1236, 315, ORANGE, 2.2, None, 9))
    s.append(arrow(gx + gw, gy + gh / 2, 1466, gy + gh / 2, GREEN, 2.2, None, 9))
    s.append(text(gx + gw + 14, gy + gh / 2 - 10, "是", 12.5, GREEN, 600))
    s.append(arrow(gx + gw / 2, gy + gh, gx + gw / 2, 466, RED, 2.2, "6 5", 9))
    s.append(text(gx + gw / 2 + 14, gy + gh + 28, "否 / 边界 / 签核", 12.5, RED))

    # calibration loop
    s.append(poly([(1420, 580), (1420, 598), (210, 598), (210, 414)], RED, 1.8, "6 5"))
    s.append(arrow(210, 598, 210, 414, RED, 1.8, None, 8))
    s.append(pill(800, 598, "周期校准 · 版本回归", 12.5, RED))

    # bottom panel
    py = 620
    s.append(rect(60, py, 1560, 240, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(90, py + 36, "路线选择与接口", 20, INK, 700))
    s.append(text(90, py + 62, "同一套契约，不同抽象层级；先选路线，再谈 95%。", 13.0, MUTED))

    # table
    s.append(text(90, py + 98, "场景", 13.5, MUTED, 600))
    s.append(text(430, py + 98, "首选", 13.5, MUTED, 600))
    rows = [
        ("跨 PDK 早期探索", "A. gm/ID 表"),
        ("固定 PDK、海量候选筛选", "B-L2 电路代理"),
        ("AC / 瞬态 / 噪声精度", "SPICE 或 B-L1"),
        ("最终签核", "SPICE"),
    ]
    for i, (a, b) in enumerate(rows):
        ry = py + 128 + i * 26
        s.append(text(90, ry, a, 13.2, INK))
        s.append(text(430, ry, b, 13.2, ORANGE, 600))

    # interface notes
    s.append(text(760, py + 98, "AI-friendly 的最小接口", 13.5, MUTED, 600))
    notes = [
        "列式存储：Parquet / Arrow，按器件、角落分区",
        "typed query：op_at(gm_id, L, Vds, corner, T)",
        "预测返回 mu / sigma / ood / provenance",
        "LLM 只看查询结果，不看整张表",
    ]
    for i, note in enumerate(notes):
        s.append(text(760, py + 128 + i * 26, "· " + note, 13.0, INK))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)



def netlist_semantics():
    W, H = 1680, 940
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "网表语义层：让 AI 看见设计意图",
        "原理图角色标注 → netlist + roles.yaml → 校验 → 角色级修改；名字是提示，manifest 是事实。",
    ))

    # Column 1: schematic intent
    s.append(rect(50, 180, 270, 390, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(70, 214, "原理图 / 设计意图", 17, INK, 700))
    chips = [
        ("input_pair", "差分输入对", BLUE, BLUE_BG),
        ("current_mirror", "电流镜", PURPLE, PURPLE_BG),
        ("cascode", "共源共栅", AMBER, AMBER_BG),
        ("output_stage", "输出级", GREEN, GREEN_BG),
        ("enable_switch", "使能开关", RED, RED_BG),
        ("adj_switch", "ADJ 开关", ORANGE, ORANGE_BG),
        ("dummy", "dummy", MUTED, GRAY_BG),
    ]
    for i, (role, label, color, bg) in enumerate(chips):
        cy = 236 + i * 42
        s.append(rect(70, cy, 230, 34, bg, color, 1.2, 8))
        s.append(rect(70, cy, 5, 34, color, "none", 0, 2))
        s.append(text(86, cy + 22, role, 12.8, color, 600, font=MONO))
        s.append(text(196, cy + 22, label, 11.2, MUTED))
    s.append(text(70, 552, "角色的含义由 spec/device-roles.yaml 定义", 10.8, FAINT))

    # Column 2: netlist + manifest
    s.append(rect(370, 180, 380, 160, WHITE, "#d5dde7", 1.2, 12))
    s.append(text(390, 210, "netlist.cir", 16, INK, 700, font=MONO))
    s.append(text(700, 210, "电气事实", 11.5, FAINT, anchor="end"))
    netlist_lines = [
        "MDP_1  dp   vinp tail vss nmos",
        "MDP_2  n1   vinn tail vss nmos",
        "MMIR_1 dp   dp   vdd vdd pmos",
        "MMIR_2 n1   dp   vdd vdd pmos",
        "MEN_1  nbias en  vss vss nmos",
    ]
    for i, line in enumerate(netlist_lines):
        s.append(text(388, 238 + i * 19, line, 10.8, INK, font=MONO))
    s.append(text(388, 328, "角色名只是提示，不是 schema", 10.2, FAINT))

    s.append(rect(370, 355, 380, 215, WHITE, "#d5dde7", 1.2, 12))
    s.append(text(390, 385, "roles.yaml", 16, INK, 700, font=MONO))
    s.append(text(700, 385, "语义事实", 11.5, FAINT, anchor="end"))
    yaml_lines = [
        "schema_version: 0.1.0",
        "topology: two-stage-opamp-v1",
        "blocks:",
        "  - id: dp",
        "    role: input_pair",
        "    devices: [MDP_1, MDP_2]",
        "    match: {same_wl: true}",
        "devices:",
        "  MDP_1: {role: input_pair, block: dp}",
    ]
    for i, line in enumerate(yaml_lines):
        s.append(text(388, 412 + i * 17, line, 10.2, INK, font=MONO))
    s.append(text(388, 562, "manifest 是事实；inline comment 只是可读性", 9.8, FAINT))

    # Column 3: validator
    s.append(rect(800, 180, 300, 390, AMBER_BG, AMBER, 1.4, 14))
    s.append(text(820, 214, "validator", 17, AMBER, 700, font=MONO))
    s.append(text(820, 238, "声明的角色 vs 拓扑事实", 11.5, MUTED))
    checks = [
        "每个器件都有角色",
        "角色在受控词表中",
        "对管 W/L 一致",
        "镜像比 = W/L 比",
        "开关 / dummy 不被调",
        "hash 与网表一致",
    ]
    for i, check in enumerate(checks):
        s.append(text(820, 276 + i * 34, "✓", 13, GREEN, 700))
        s.append(text(840, 276 + i * 34, check, 12.2, INK))
    s.append(f'<line x1="820" y1="490" x2="1080" y2="490" stroke="#e2c9a0" stroke-width="1"/>')
    s.append(text(820, 516, "任一失败 → 拒绝 patch", 12.8, RED, 700))
    s.append(text(820, 540, "不是“看起来像”，是“可检查”", 10.8, MUTED))

    # Column 4: role map
    s.append(rect(1150, 180, 240, 390, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(1170, 214, "role map", 17, INK, 700, font=MONO))
    s.append(text(1170, 238, "给 agent 的紧凑视图", 11.5, FAINT))
    role_lines = [
        "dp: gm/ID=10.2",
        "    W/L=20/0.5",
        "mirror: ratio=1.0",
        "out: W/L=40/0.5",
        "en: digital, fixed",
        "dummy: fixed",
        "comp: 1.2p + 1k",
    ]
    for i, line in enumerate(role_lines):
        s.append(text(1168, 278 + i * 32, line, 10.4, INK, font=MONO))
    s.append(text(1170, 528, "不是全量网表", 11.2, FAINT))

    # Column 5: agent tools
    s.append(rect(1430, 180, 200, 390, TEAL_BG, TEAL, 1.4, 14))
    s.append(text(1448, 214, "agent tools", 17, TEAL, 700, font=MONO))
    tools = ["resize_group()", "set_bias()", "validate_roles()", "apply_patch()", "query_devices()"]
    for i, tool in enumerate(tools):
        s.append(text(1448, 254 + i * 34, tool, 10.2, INK, font=MONO))
    s.append(text(1448, 462, "只做角色级修改", 10.8, MUTED))
    s.append(text(1448, 484, "不直接改文本", 10.8, MUTED))

    # Arrows
    s.append(arrow(320, 370, 366, 370, MUTED, 2.0, None, 8))
    s.append(text(326, 356, "导出", 10.5, FAINT))
    s.append(arrow(750, 370, 796, 370, MUTED, 2.0, None, 8))
    s.append(text(756, 356, "校验", 10.5, FAINT))
    s.append(arrow(1100, 370, 1146, 370, MUTED, 2.0, None, 8))
    s.append(text(1106, 356, "摘要", 10.5, FAINT))
    s.append(arrow(1390, 370, 1426, 370, MUTED, 2.0, None, 8))
    s.append(text(1388, 356, "调用", 10.5, FAINT))

    # Feedback: role-level patch
    s.append(poly([(1530, 570), (1530, 588), (560, 588), (560, 574)], TEAL, 2.0, "6 5"))
    s.append(arrow(560, 588, 560, 574, TEAL, 2.0, None, 8))
    s.append(pill(1045, 588, "role-level patch：重新生成 netlist / roles", 12.0, TEAL))

    # Bottom panel
    py = 620
    s.append(rect(60, py, 1560, 270, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(90, py + 34, "一个例子：两级运放", 19, INK, 700))
    s.append(text(90, py + 58, "同一张表既给人看，也给工具查；每一条约束都能落到 validator 上。", 11.8, MUTED))

    # table
    s.append(text(90, py + 88, "实例", 11.8, FAINT, 600))
    s.append(text(280, py + 88, "角色", 11.8, FAINT, 600))
    s.append(text(500, py + 88, "约束", 11.8, FAINT, 600))
    rows = [
        ("MDP_1/2", "input_pair", "same W/L, common centroid"),
        ("MMIR_1/2", "current_mirror", "ratio 1.0"),
        ("MEN_1", "enable_switch", "digital, fixed"),
        ("MADJ_1/2", "adj_switch", "discrete, fixed"),
        ("MDUM_1/2", "dummy", "fixed, no signal"),
        ("MOUT_1", "output_stage", "drives load"),
    ]
    for i, (inst, role, cons) in enumerate(rows):
        yy = py + 116 + i * 24
        s.append(text(90, yy, inst, 11.2, INK, font=MONO))
        s.append(text(280, yy, role, 11.2, ORANGE, 600, font=MONO))
        s.append(text(500, yy, cons, 11.0, MUTED))

    # right notes
    s.append(text(820, py + 88, "为什么名字不够", 12.5, INK, 700))
    notes = [
        "名字会漂移：M1 / MIR / MIRROR 可能指同一件事",
        "名字会撒谎：叫 mirror 的管子不一定 diode-connected",
        "名字不带约束：匹配、比例、开关的离散性",
        "所以：manifest 是事实，validator 是仲裁，名字只是提示",
    ]
    for i, note in enumerate(notes):
        s.append(text(820, py + 116 + i * 24, "· " + note, 11.0, MUTED))

    s.append(text(820, py + 228, "与自动标注的关系：GANA / AMSnet-q 自动推断；Analog-DB 把子块做成命名参数。", 10.5, FAINT))
    s.append(text(820, py + 250, "这里做的是：显式声明 + 校验 + 工具原生。", 10.5, FAINT))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)



def area_aware_loop():
    W, H = 1680, 960
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "面积进入闭环：从角色到 area-aware Pareto",
        "先估面积，再花仿真；面积是带区间的约束，不是事后统计。",
    ))

    # A. candidate + roles
    s.append(rect(50, 180, 280, 300, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(70, 214, "候选 + 角色", 17, INK, 700))
    s.append(text(70, 238, "netlist.cir + roles.yaml", 10.8, FAINT, font=MONO))
    chips = [
        ("input_pair", BLUE, BLUE_BG),
        ("current_mirror", PURPLE, PURPLE_BG),
        ("cascode", AMBER, AMBER_BG),
        ("output_stage", GREEN, GREEN_BG),
        ("dummy", MUTED, GRAY_BG),
        ("compensation", ORANGE, ORANGE_BG),
    ]
    for i, (role, color, bg) in enumerate(chips):
        cy = 262 + i * 32
        s.append(rect(70, cy, 240, 24, bg, color, 1.0, 6))
        s.append(text(82, cy + 17, role, 10.8, color, 600, font=MONO))
    s.append(text(70, 462, "W/L, nf, m, match, group", 10.2, FAINT))

    # B. area estimator
    s.append(rect(370, 180, 390, 300, AMBER_BG, AMBER, 1.4, 14))
    s.append(text(390, 214, "面积估算（规则 + 角色）", 17, AMBER, 700))
    s.append(text(390, 238, "每一项都能追溯到 rule key", 10.8, MUTED))
    rows = [
        ("core", "W · L · nf · m"),
        ("+ S/D + contact", "finger pitch / OD"),
        ("+ well + guard ring", "critical roles"),
        ("+ matching dummies", "group / centroid"),
        ("+ routing", "device / block"),
        ("+ periphery + reserve", "block"),
    ]
    for i, (left, right) in enumerate(rows):
        yy = 272 + i * 34
        s.append(text(390, yy, left, 11.6, INK, 600))
        s.append(text(600, yy, right, 10.4, MUTED, font=MONO))
    s.append(text(390, 464, "rule pack: generic-180 · confidence: educational", 9.8, FAINT))

    # C. area gate
    s.append(rect(800, 180, 330, 300, ORANGE_BG, ORANGE, 1.4, 14))
    s.append(text(820, 214, "面积门", 17, ORANGE, 700))
    s.append(text(820, 238, "low / nominal / high", 10.8, MUTED, font=MONO))
    gates = [
        ("high ≤ budget", "PASS", GREEN),
        ("low > budget", "REJECT", RED),
        ("overlap", "UNCERTAIN", AMBER),
    ]
    for i, (cond, outcome, color) in enumerate(gates):
        yy = 280 + i * 54
        s.append(text(820, yy, cond, 11.6, INK, font=MONO))
        s.append(text(1080, yy, "→ " + outcome, 12.0, color, 700, "end"))
    s.append(f'<line x1="820" y1="438" x2="1100" y2="438" stroke="#e2c9a0" stroke-width="1"/>')
    s.append(text(820, 462, "guardband: budget / (1 + g)", 10.4, MUTED, font=MONO))

    # D. Pareto + SPICE
    s.append(rect(1170, 180, 460, 300, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(1190, 214, "area-aware Pareto", 17, INK, 700))
    s.append(text(1190, 238, "面积不是标量：不压成加权和", 10.8, FAINT))
    # simple axes
    ox, oy = 1210, 430
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{ox+360}" y2="{oy}" stroke="#c9d2de" stroke-width="1.4"/>')
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy-160}" stroke="#c9d2de" stroke-width="1.4"/>')
    s.append(text(1560, 448, "area →", 10.5, MUTED, anchor="end"))
    s.append(text(1200, 285, "power ↑", 10.5, MUTED, anchor="end"))
    points = [(1260, 380, GREEN), (1320, 340, GREEN), (1410, 310, GREEN), (1500, 270, AMBER), (1540, 250, AMBER)]
    for px, py, color in points:
        s.append(circle(px, py, 6, color, WHITE, 1.2))
    s.append(text(1410, 260, "frontier", 10.2, MUTED, anchor="middle"))
    s.append(text(1190, 466, "SPICE 确认 → handoff", 11.2, INK, 600))

    # arrows top row
    s.append(arrow(330, 330, 366, 330, MUTED, 2.0, None, 8))
    s.append(arrow(760, 330, 796, 330, MUTED, 2.0, None, 8))
    s.append(arrow(1130, 330, 1166, 330, MUTED, 2.0, None, 8))

    # handoff panel
    py = 540
    s.append(rect(60, py, 1560, 160, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(90, py + 30, "handoff 到 layout", 18, INK, 700))
    s.append(text(90, py + 52, "角色不只用于 sizing，也用于 floorplan 约束和 layout delta。", 10.8, MUTED))

    hboxes = [
        ("roles.yaml + netlist", "device / group / match", TEAL, TEAL_BG),
        ("floorplan intent", "symmetry · bands · channels", GREEN, GREEN_BG),
        ("layout delta", "dummy · decap · finger split", AMBER, AMBER_BG),
        ("review", "owner · reason · area", ORANGE, ORANGE_BG),
        ("new case", "回到闭环重新评估", RED, RED_BG),
    ]
    for i, (title, sub, color, bg) in enumerate(hboxes):
        bx = 90 + i * 290
        s.append(rect(bx, py + 70, 250, 60, bg, color, 1.2, 10))
        s.append(text(bx + 12, py + 94, title, 12.0, color, 700, font=MONO))
        s.append(text(bx + 12, py + 116, sub, 9.8, MUTED))
        if i < len(hboxes) - 1:
            s.append(arrow(bx + 250, py + 100, bx + 286, py + 100, MUTED, 1.6, None, 7))

    # feedback: new case -> candidate
    s.append(poly([(1500, py + 100), (1620, py + 100), (1620, 510), (190, 510), (190, 484)], RED, 1.8, "6 5"))
    s.append(arrow(190, 510, 190, 484, RED, 1.8, None, 8))
    s.append(pill(900, 510, "accepted delta → 新 case", 11.5, RED))

    # bottom panel: boundaries
    by = 730
    s.append(rect(60, by, 1560, 190, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(90, by + 30, "面积模型的边界与用法", 17, INK, 700))
    cols = [
        ("会被低估的", [
            "well sharing / guard ring",
            "routing / block periphery",
            "matching dummies",
            "PEX-fix reserve",
        ], RED),
        ("这层不覆盖", [
            "DRC / LVS / PEX",
            "metal / EM / thermal",
            "pad ring / ESD",
            "exact placement",
        ], MUTED),
        ("怎么用", [
            "low / nominal / high",
            "三值 gate + guardband",
            "Pareto，不加权求和",
            "delta 作为新 case",
        ], GREEN),
    ]
    for i, (title, items, color) in enumerate(cols):
        cx = 90 + i * 500
        s.append(text(cx, by + 62, title, 12.5, color, 700))
        for j, item in enumerate(items):
            s.append(text(cx, by + 88 + j * 22, "· " + item, 10.4, INK))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)



def asst_execution():
    W, H = 1680, 940
    s = [svg_open(W, H)]
    s.append(header(
        W,
        "ASST：AI、脚本、人各做什么",
        "AI 发意图，ASST 固化 CLI；一张 CSV/Excel 是唯一真相源。",
    ))

    # Human
    s.append(rect(50, 180, 300, 200, BLUE_BG, BLUE, 1.4, 14))
    s.append(text(70, 214, "人", 18, BLUE, 700))
    human = ["CSV / Excel 配置", "PVT / 参数矩阵", "measure 定义", "签核 / 例外"]
    for i, item in enumerate(human):
        s.append(text(70, 248 + i * 28, "· " + item, 12.0, INK))
    s.append(text(70, 366, "可手改，一键重生成", 10.5, FAINT))

    # AI
    s.append(rect(50, 420, 300, 200, GREEN_BG, GREEN, 1.4, 14))
    s.append(text(70, 454, "AI", 18, GREEN, 700))
    ai = ["选策略 / 提候选", "读失败 / 定下一步", "汇总 / 建议", "预算 / 角色补丁"]
    for i, item in enumerate(ai):
        s.append(text(70, 488 + i * 28, "· " + item, 12.0, INK))
    s.append(text(70, 606, "只调 typed tools；不直接调 CLI", 10.5, RED))

    # ASST container
    s.append(rect(410, 180, 620, 440, AMBER_BG, AMBER, 1.5, 14))
    s.append(text(440, 214, "ASST 执行层", 19, AMBER, 700))
    s.append(text(440, 238, "SSOT: config.csv/xlsx → config.json + sha256 → plan", 10.4, MUTED))
    stages = [
        ("validate", "CSV/Excel → schema", "配置校验"),
        ("plan", "run dir · PVT matrix · hash", "可重放计划"),
        ("run", "adapter · license · logs", "启动仿真"),
        ("collect", "measure contract → metrics", "结果解析"),
        ("summarize", "Excel · archive · compare", "汇总归档"),
    ]
    for i, (name, detail, zh) in enumerate(stages):
        yy = 258 + i * 72
        s.append(rect(440, yy, 540, 54, WHITE, AMBER, 1.2, 10))
        s.append(text(456, yy + 22, name, 12.5, AMBER, 700, font=MONO))
        s.append(text(456, yy + 43, detail, 10.2, INK, font=MONO))
        s.append(text(960, yy + 34, zh, 10.8, MUTED, anchor="end"))
        if i < len(stages) - 1:
            s.append(arrow(710, yy + 54, 710, yy + 68, AMBER, 1.8, None, 7))

    # Simulators
    s.append(rect(1100, 180, 260, 220, PURPLE_BG, PURPLE, 1.4, 14))
    s.append(text(1120, 214, "仿真器", 18, PURPLE, 700))
    for i, item in enumerate(["Spectre", "ALPS", "XA"]):
        s.append(text(1120, 250 + i * 30, item, 12.5, INK, font=MONO))
    s.append(text(1120, 374, "命令模板由 ASST 固化", 10.2, FAINT))

    # Results
    s.append(rect(1100, 460, 260, 160, TEAL_BG, TEAL, 1.4, 14))
    s.append(text(1120, 494, "结果", 18, TEAL, 700))
    for i, item in enumerate(["metrics.json", "summary.xlsx", "run archive"]):
        s.append(text(1120, 528 + i * 26, "· " + item, 11.2, INK, font=MONO))
    s.append(text(1120, 608, "config / netlist / plan hash", 9.6, FAINT))

    # Arrows
    s.append(arrow(350, 280, 406, 280, BLUE, 2.2, None, 9))
    s.append(text(362, 266, "配置", 10.5, FAINT))
    s.append(arrow(350, 520, 406, 520, GREEN, 2.0, "6 5", 8))
    s.append(text(362, 506, "tools", 10.5, FAINT))

    # run -> simulators
    s.append(poly([(980, 401), (1030, 401), (1030, 300), (1096, 300)], PURPLE, 1.9))
    s.append(arrow(1030, 300, 1096, 300, PURPLE, 1.9, None, 8))
    s.append(text(1034, 291, "run", 10.2, PURPLE))
    # simulators -> collect
    s.append(poly([(1150, 400), (1050, 400), (1050, 470), (984, 470)], PURPLE, 1.6, "5 4"))
    s.append(arrow(1050, 470, 984, 470, PURPLE, 1.6, None, 7))
    s.append(text(1054, 462, "results", 10.2, PURPLE))
    # summarize -> results
    s.append(arrow(980, 545, 1096, 545, TEAL, 2.0, None, 9))
    s.append(text(1002, 535, "Excel", 10.5, TEAL))

    # SSOT band
    s.append(rect(410, 628, 620, 34, GRAY_BG, "#cfd8e3", 1.0, 8))
    s.append(text(430, 650, "AI 只能改 config；run 中途改配置 → 新 snapshot / 新 plan", 10.2, INK))

    # Bottom panel
    py = 680
    s.append(rect(60, py, 1560, 220, WHITE, "#d5dde7", 1.2, 14))
    s.append(text(90, py + 32, "分工：AI 做什么，脚本做什么，人做什么", 19, INK, 700))
    cols = [
        ("人", BLUE, [
            "定目标 / 拓扑 / 约束",
            "PVT / 参数矩阵 / measure",
            "审核异常，签核",
            "接受或拒绝结果",
        ]),
        ("脚本（ASST）", AMBER, [
            "校验配置，生成 run dir",
            "设置环境/license，启动仿真",
            "解析 measure，汇总 Excel",
            "归档、哈希、重试、日志",
        ]),
        ("AI", GREEN, [
            "选策略，提候选",
            "读失败，定下一步",
            "分配预算，做角色补丁",
            "不碰 CLI，不持数值状态",
        ]),
    ]
    for i, (title, color, items) in enumerate(cols):
        cx = 90 + i * 500
        s.append(text(cx, py + 70, title, 13.5, color, 700))
        for j, item in enumerate(items):
            s.append(text(cx, py + 98 + j * 24, "· " + item, 10.8, INK))

    s.append(footer(W, H))
    s.append("</svg>")
    return "".join(s)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    PNG.mkdir(parents=True, exist_ok=True)

    figures = {
        "architecture": architecture(),
        "fast-verification": fast_verification(),
        "mcu-mapping": mcu_mapping(),
        "pdk-fastpath": pdk_fastpath(),
        "netlist-semantics": netlist_semantics(),
        "area-aware-loop": area_aware_loop(),
        "asst-execution": asst_execution(),
    }
    for name, svg in figures.items():
        path = OUT / f"{name}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path.relative_to(ROOT)} ({len(svg)} bytes)")

    try:
        import cairosvg
    except ImportError:
        print("cairosvg not installed; SVG written, PNG skipped", file=sys.stderr)
        return

    for name in figures:
        src = OUT / f"{name}.svg"
        dst = PNG / f"{name}.png"
        cairosvg.svg2png(url=str(src), write_to=str(dst), scale=2)
        print(f"wrote {dst.relative_to(ROOT)}")


import sys

if __name__ == "__main__":
    main()