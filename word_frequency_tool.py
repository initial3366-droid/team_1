#!/usr/bin/env python3
"""第 28 题：词频统计工具。

功能：
1. 读取文本文件并统计单词/词语频率；
2. 支持停用词过滤；
3. 将统计结果保存到 CSV；
4. 优先使用 wordcloud 库生成词云图；如果环境未安装 wordcloud，自动降级生成
   可直接打开的 SVG 词云图，保证作业在纯标准库环境也能运行。
"""

from __future__ import annotations

import argparse
import csv
import html
import math
import random
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

DEFAULT_STOPWORDS = {
    "的",
    "了",
    "和",
    "是",
    "在",
    "对",
    "与",
    "及",
    "并",
    "等",
    "a",
    "an",
    "and",
    "are",
    "as",
    "for",
    "in",
    "is",
    "of",
    "on",
    "the",
    "to",
}

TOKEN_PATTERN = re.compile(r"[\u4e00-\u9fff]+|[A-Za-z][A-Za-z0-9_+#.-]*|\d+(?:\.\d+)?")


def read_text(path: Path) -> str:
    """读取 UTF-8 文本文件。"""
    return path.read_text(encoding="utf-8")


def load_stopwords(path: Path | None) -> set[str]:
    """加载停用词；未提供文件时使用内置常用停用词。"""
    stopwords = set(DEFAULT_STOPWORDS)
    if path and path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                stopwords.add(word.lower())
    return stopwords


def tokenize(text: str) -> list[str]:
    """分词：优先使用 jieba；没有安装时使用正则分词兜底。"""
    try:
        import jieba  # type: ignore
    except ImportError:
        return TOKEN_PATTERN.findall(text)

    return [word.strip() for word in jieba.cut(text) if word.strip()]


def count_words(text: str, stopwords: set[str], min_len: int = 1) -> Counter[str]:
    """统计词频，并过滤停用词、空白符和过短词。"""
    counter: Counter[str] = Counter()
    for token in tokenize(text):
        word = token.strip()
        normalized = word.lower()
        if len(word) < min_len or normalized in stopwords or word in stopwords:
            continue
        if not TOKEN_PATTERN.fullmatch(word):
            continue
        counter[word] += 1
    return counter


def save_csv(counter: Counter[str], csv_path: Path, top_n: int | None = None) -> None:
    """按频率降序保存 CSV。"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rows = counter.most_common(top_n)
    with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["word", "frequency"])
        writer.writerows(rows)


def find_font() -> str | None:
    """自动查找常见中文字体，找不到时返回 None。"""
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    return next((font for font in candidates if Path(font).exists()), None)


def generate_wordcloud_png(
    counter: Counter[str], image_path: Path, font_path: str | None, width: int, height: int
) -> bool:
    """使用 wordcloud 库生成 PNG/JPG 词云；未安装库时返回 False。"""
    try:
        from wordcloud import WordCloud  # type: ignore
    except ImportError:
        return False

    image_path.parent.mkdir(parents=True, exist_ok=True)
    wc = WordCloud(
        width=width,
        height=height,
        background_color="white",
        font_path=font_path,
        colormap="viridis",
        prefer_horizontal=0.88,
        random_state=28,
        max_words=120,
        margin=3,
    )
    wc.generate_from_frequencies(dict(counter))
    wc.to_file(str(image_path))
    return True


def spiral_positions(width: int, height: int, count: int) -> Iterable[tuple[float, float, float]]:
    """生成由中心向外扩散且尽量避免重叠的美观词云坐标。"""
    center_x, center_y = width / 2, height / 2 + 18
    if count <= 0:
        return

    # 高频词放在中心，其余词按椭圆环绕排布，既有词云效果又不容易互相遮挡。
    yield center_x, center_y, 0
    ring_specs = [
        (8, width * 0.20, height * 0.16),
        (16, width * 0.32, height * 0.27),
        (28, width * 0.42, height * 0.36),
        (48, width * 0.48, height * 0.42),
    ]
    produced = 1
    for ring_index, (slots, radius_x, radius_y) in enumerate(ring_specs):
        if produced >= count:
            break
        offset = ring_index * math.pi / 9
        for slot in range(slots):
            if produced >= count:
                break
            angle = offset + 2 * math.pi * slot / slots
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            rotate = 0 if produced % 4 else (-10 if produced % 8 else 10)
            yield max(80, min(width - 80, x)), max(90, min(height - 70, y)), rotate
            produced += 1


def generate_wordcloud_svg(counter: Counter[str], image_path: Path, width: int, height: int) -> None:
    """标准库 SVG 兜底词云：即使没有安装 wordcloud 也能生成实物图。"""
    image_path.parent.mkdir(parents=True, exist_ok=True)
    rows = counter.most_common(100)
    if not rows:
        rows = [("无有效词语", 1)]
    max_frequency = rows[0][1]
    min_frequency = rows[-1][1]
    span = max(max_frequency - min_frequency, 1)
    rng = random.Random(28)
    palette = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0f766e", "#1f2937"]

    text_nodes: list[str] = []
    for (word, frequency), (x, y, rotate) in zip(rows, spiral_positions(width, height, len(rows))):
        weight = (frequency - min_frequency) / span
        font_size = 18 + int(54 * math.sqrt(weight))
        color = palette[rng.randrange(len(palette))]
        safe_word = html.escape(word)
        text_nodes.append(
            f'<text x="{x:.1f}" y="{y:.1f}" font-size="{font_size}" fill="{color}" '
            f'font-family="Microsoft YaHei, SimHei, PingFang SC, Noto Sans CJK SC, Arial, sans-serif" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'transform="rotate({rotate:.1f} {x:.1f} {y:.1f})">{safe_word}</text>'
        )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#f8fafc"/>
  <text x="{width / 2}" y="42" font-size="28" font-weight="700" fill="#111827" text-anchor="middle" font-family="Microsoft YaHei, SimHei, Arial, sans-serif">第28题：词频统计词云图</text>
  <g opacity="0.96">
    {chr(10).join(text_nodes)}
  </g>
</svg>
'''
    image_path.write_text(svg, encoding="utf-8")


def generate_wordcloud(counter: Counter[str], image_path: Path, font_path: str | None, width: int, height: int) -> Path:
    """生成词云图；PNG/JPG 使用 wordcloud，其他或缺库时输出 SVG。"""
    suffix = image_path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"} and generate_wordcloud_png(counter, image_path, font_path, width, height):
        return image_path

    svg_path = image_path if suffix == ".svg" else image_path.with_suffix(".svg")
    generate_wordcloud_svg(counter, svg_path, width, height)
    return svg_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="第28题：读取文本、统计词频、生成词云、导出CSV。")
    parser.add_argument("-i", "--input", type=Path, required=True, help="输入文本文件路径")
    parser.add_argument("-s", "--stopwords", type=Path, help="停用词文件路径，每行一个词")
    parser.add_argument("-c", "--csv", type=Path, default=Path("output/word_frequency.csv"), help="输出CSV路径")
    parser.add_argument("-o", "--image", type=Path, default=Path("output/wordcloud.png"), help="输出词云图片路径")
    parser.add_argument("--font", dest="font_path", help="中文字体路径；不填则自动查找")
    parser.add_argument("--top", type=int, default=80, help="CSV和词云最多保留的词数")
    parser.add_argument("--min-len", type=int, default=1, help="最短词长")
    parser.add_argument("--width", type=int, default=1200, help="词云宽度")
    parser.add_argument("--height", type=int, default=800, help="词云高度")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    text = read_text(args.input)
    stopwords = load_stopwords(args.stopwords)
    counter = count_words(text, stopwords, min_len=args.min_len)
    if args.top:
        counter = Counter(dict(counter.most_common(args.top)))

    save_csv(counter, args.csv, top_n=args.top)
    actual_image = generate_wordcloud(
        counter=counter,
        image_path=args.image,
        font_path=args.font_path or find_font(),
        width=args.width,
        height=args.height,
    )

    print(f"已统计 {len(counter)} 个词语")
    print(f"CSV 已保存：{args.csv}")
    print(f"词云图已保存：{actual_image}")


if __name__ == "__main__":
    main()
