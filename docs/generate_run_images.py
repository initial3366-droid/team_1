"""Generate SVG run screenshots for the dormitory management system."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Iterable

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dormitory_management_system import DormitoryManager  # noqa: E402


OUTPUT_DIR = Path(__file__).resolve().parent / "run_images"


def text(x: int, y: int, value: object, size: int = 15, color: str = "#1f2937", weight: int = 400) -> str:
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{escape(str(value))}</text>'


def rect(x: int, y: int, width: int, height: int, fill: str, stroke: str = "#cbd5e1", radius: int = 8) -> str:
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>'


def shell(title: str, subtitle: str, content: Iterable[str]) -> str:
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="720" viewBox="0 0 1180 720">',
            '<rect width="1180" height="720" fill="#eef6ff"/>',
            rect(24, 20, 1132, 680, "#f8fbff", "#bfdbfe", 18),
            text(54, 70, title, 28, "#0f5ea8", 700),
            text(54, 102, subtitle, 16, "#475569"),
            *content,
            '</svg>',
        ]
    )


def table_rows(assignments) -> list[str]:
    rows = [rect(360, 165, 760, 42, "#dbeafe", "#bfdbfe", 0)]
    for x, label in [(378, "宿舍位置"), (540, "学号"), (670, "姓名"), (760, "性别"), (830, "专业"), (990, "电话")]:
        rows.append(text(x, 192, label, 14, "#075985", 700))
    y = 226
    for item in assignments[:8]:
        rows.append(rect(360, y - 23, 760, 34, "#ffffff", "#d7e3f3", 0))
        for x, value in [
            (378, item.place),
            (540, item.student_id),
            (670, item.name),
            (760, item.gender),
            (830, item.major),
            (990, item.phone),
        ]:
            rows.append(text(x, y, value, 14))
        y += 36
    return rows


def form_panel(selected) -> list[str]:
    items = [rect(54, 130, 270, 525, "#ffffff"), text(76, 166, "宿舍分配表单", 20, "#111827", 700)]
    fields = [
        ("楼号", selected.building),
        ("房间号", selected.room),
        ("床位", selected.bed),
        ("学号", selected.student_id),
        ("姓名", selected.name),
        ("性别", selected.gender),
        ("专业", selected.major),
        ("电话", selected.phone),
    ]
    y = 195
    for label, value in fields:
        items.append(text(76, y, label, 14, "#475569", 700))
        items.append(rect(130, y - 21, 170, 30, "#ffffff" if label not in {"楼号", "房间号", "床位"} else "#eff6ff", "#bfdbfe"))
        items.append(text(145, y, value, 13))
        y += 43
    items.extend(
        [
            rect(76, 555, 224, 40, "#2563eb", "#2563eb"),
            text(125, 581, "分配/更新床位", 16, "#ffffff", 700),
            rect(76, 608, 224, 40, "#f97316", "#f97316"),
            text(120, 634, "删除当前床位记录", 16, "#ffffff", 700),
        ]
    )
    return items


def roster_screen(manager: DormitoryManager) -> str:
    selected = manager.search_students()[0]
    content = [*form_panel(selected), rect(340, 130, 800, 525, "#ffffff"), text(360, 153, "住宿名单：启动后自动读取 dormitory_data.csv", 18, "#1d4ed8", 700)]
    content.extend(table_rows(manager.search_students()))
    content.append(text(360, 610, f"状态栏：住宿 {len(manager.assignments)} 人，剩余床位 {len(manager.vacant_beds())} 个", 15, "#475569"))
    return shell("运行图片 1：首页住宿名单", "展示程序启动后读取样例数据的主界面", content)


def vacancy_screen(manager: DormitoryManager) -> str:
    vacancies = manager.vacant_beds("1号楼", "101")[:10]
    content = [*form_panel(manager.search_students()[0]), rect(340, 130, 800, 525, "#ffffff"), text(360, 153, "空余床位查询：楼号=1号楼，房间关键字=101", 18, "#166534", 700)]
    content.append(rect(360, 178, 260, 36, "#f0fdf4", "#bbf7d0"))
    content.append(text(378, 201, "查询条件：1号楼 / 101", 15, "#166534"))
    y = 250
    for building, room, bed in vacancies:
        content.append(rect(380, y - 24, 280, 36, "#ffffff", "#bbf7d0"))
        content.append(text(405, y, f"{building}  {room}  {bed}", 15, "#166534", 700))
        y += 44
    content.append(text(720, 285, "点击空床位后会自动回填左侧楼号、房间号、床位。", 16, "#475569"))
    return shell("运行图片 2：空余床位查询", "展示按楼号和房间号查询可用床位", content)


def search_screen(manager: DormitoryManager) -> str:
    rows = manager.search_students("软件工程")
    content = [*form_panel(rows[0]), rect(340, 130, 800, 525, "#ffffff"), text(360, 153, "关键词搜索：软件工程", 18, "#1d4ed8", 700)]
    content.extend(table_rows(rows))
    content.append(text(360, 380, f"搜索结果：{len(rows)} 条，可点击任意行回填并修改。", 16, "#475569"))
    return shell("运行图片 3：住宿名单搜索", "展示按专业/姓名/学号/电话等关键词检索", content)


def export_screen(manager: DormitoryManager) -> str:
    content = [*form_panel(manager.search_students()[0]), rect(340, 130, 800, 525, "#ffffff"), text(360, 153, "导出住宿名单", 18, "#9a3412", 700)]
    content.extend(
        [
            rect(430, 220, 560, 260, "#fff7ed", "#fed7aa", 16),
            text(470, 275, "点击“导出住宿名单”按钮", 22, "#9a3412", 700),
            text(470, 322, "选择保存位置后生成 CSV 文件：住宿名单.csv", 17, "#9a3412"),
            text(470, 370, "导出字段：楼号、房间号、床位、学号、姓名、性别、专业、电话", 15, "#7c2d12"),
            text(470, 420, f"当前样例数据可导出 {len(manager.assignments)} 条住宿记录。", 17, "#7c2d12", 700),
        ]
    )
    return shell("运行图片 4：导出住宿名单", "展示 CSV 导出功能和导出内容", content)


def main() -> None:
    manager = DormitoryManager()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        "01_home_roster.svg": roster_screen(manager),
        "02_vacancy_query.svg": vacancy_screen(manager),
        "03_search_results.svg": search_screen(manager),
        "04_export_roster.svg": export_screen(manager),
    }
    for name, svg in files.items():
        (OUTPUT_DIR / name).write_text(svg, encoding="utf-8")
        print(OUTPUT_DIR / name)


if __name__ == "__main__":
    main()
