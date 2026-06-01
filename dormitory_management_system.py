"""学生宿舍管理系统（第47题）

功能：
1. 管理宿舍分配（楼号、房间号、床位）。
2. 查询空余床位。
3. 数据保存到 CSV 文件。
4. 支持导出住宿名单。

运行图形界面：
    python dormitory_management_system.py

命令行自检：
    python dormitory_management_system.py --self-test
"""

from __future__ import annotations

import argparse
import csv
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Optional

import tkinter as tk
from tkinter import filedialog, messagebox, ttk


DATA_FILE = Path("dormitory_data.csv")
DEFAULT_BUILDINGS = ("1号楼", "2号楼", "3号楼", "4号楼")
DEFAULT_ROOMS = [f"{floor}{room:02d}" for floor in range(1, 7) for room in range(1, 9)]
DEFAULT_BEDS = ("1床", "2床", "3床", "4床")
CSV_COLUMNS = ["building", "room", "bed", "student_id", "name", "gender", "major", "phone"]


@dataclass
class Assignment:
    """一条住宿分配记录。"""

    building: str
    room: str
    bed: str
    student_id: str
    name: str
    gender: str
    major: str
    phone: str

    @property
    def place(self) -> str:
        return f"{self.building}-{self.room}-{self.bed}"


class DormitoryManager:
    """负责宿舍数据的增删改查和 CSV 读写。"""

    def __init__(
        self,
        data_file: Path = DATA_FILE,
        buildings: Iterable[str] = DEFAULT_BUILDINGS,
        rooms: Iterable[str] = DEFAULT_ROOMS,
        beds: Iterable[str] = DEFAULT_BEDS,
    ) -> None:
        self.data_file = Path(data_file)
        self.buildings = list(buildings)
        self.rooms = list(rooms)
        self.beds = list(beds)
        self.assignments: List[Assignment] = []
        self.load()

    def load(self) -> None:
        """从 CSV 文件加载数据；文件不存在时使用空数据。"""
        self.assignments.clear()
        if not self.data_file.exists():
            return
        with self.data_file.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                if row.get("building") and row.get("room") and row.get("bed"):
                    self.assignments.append(
                        Assignment(**{column: row.get(column, "") for column in CSV_COLUMNS})
                    )

    def save(self) -> None:
        """保存当前住宿数据到 CSV 文件。"""
        with self.data_file.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
            writer.writeheader()
            writer.writerows(asdict(item) for item in self.assignments)

    def all_beds(self) -> list[tuple[str, str, str]]:
        return [
            (building, room, bed)
            for building in self.buildings
            for room in self.rooms
            for bed in self.beds
        ]

    def occupied_keys(self) -> set[tuple[str, str, str]]:
        return {(item.building, item.room, item.bed) for item in self.assignments}

    def vacant_beds(self, building: str = "全部", room_keyword: str = "") -> list[tuple[str, str, str]]:
        """按楼号和房间关键字查询空余床位。"""
        occupied = self.occupied_keys()
        results = []
        for bed in self.all_beds():
            bed_building, bed_room, _ = bed
            if building != "全部" and bed_building != building:
                continue
            if room_keyword and room_keyword not in bed_room:
                continue
            if bed not in occupied:
                results.append(bed)
        return results

    def find_by_place(self, building: str, room: str, bed: str) -> Optional[Assignment]:
        for item in self.assignments:
            if (item.building, item.room, item.bed) == (building, room, bed):
                return item
        return None

    def add_or_update(self, assignment: Assignment) -> str:
        """添加或更新床位分配，返回操作类型。"""
        if not assignment.student_id.strip() or not assignment.name.strip():
            raise ValueError("学号和姓名不能为空。")
        existing = self.find_by_place(assignment.building, assignment.room, assignment.bed)
        if existing:
            existing.student_id = assignment.student_id
            existing.name = assignment.name
            existing.gender = assignment.gender
            existing.major = assignment.major
            existing.phone = assignment.phone
            action = "更新"
        else:
            self.assignments.append(assignment)
            action = "新增"
        self.save()
        return action

    def delete(self, building: str, room: str, bed: str) -> bool:
        before = len(self.assignments)
        self.assignments = [
            item
            for item in self.assignments
            if (item.building, item.room, item.bed) != (building, room, bed)
        ]
        changed = len(self.assignments) != before
        if changed:
            self.save()
        return changed

    def search_students(self, keyword: str = "") -> list[Assignment]:
        """按姓名、学号、专业、电话或床位关键字搜索住宿名单。"""
        keyword = keyword.strip().lower()
        if not keyword:
            return sorted(self.assignments, key=lambda item: (item.building, item.room, item.bed))
        return [
            item
            for item in self.assignments
            if keyword
            in " ".join(
                [
                    item.building,
                    item.room,
                    item.bed,
                    item.student_id,
                    item.name,
                    item.gender,
                    item.major,
                    item.phone,
                ]
            ).lower()
        ]

    def export_roster(self, target_file: Path) -> None:
        """导出住宿名单 CSV。"""
        with Path(target_file).open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["楼号", "房间号", "床位", "学号", "姓名", "性别", "专业", "电话"])
            for item in self.search_students():
                writer.writerow(
                    [
                        item.building,
                        item.room,
                        item.bed,
                        item.student_id,
                        item.name,
                        item.gender,
                        item.major,
                        item.phone,
                    ]
                )


class DormitoryApp(tk.Tk):
    """Tkinter 图形界面。"""

    def __init__(self, manager: DormitoryManager) -> None:
        super().__init__()
        self.manager = manager
        self.title("第47题：学生宿舍管理系统")
        self.geometry("1180x720")
        self.minsize(980, 620)
        self.font_size = tk.IntVar(value=11)
        self.bg_color = tk.StringVar(value="#eef6ff")
        self.configure(bg=self.bg_color.get())
        self.entries: dict[str, tk.Variable] = {}
        self._build_style()
        self._build_widgets()
        self.refresh_tables()

    def _build_style(self) -> None:
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self._apply_style()

    def _apply_style(self) -> None:
        font = ("Microsoft YaHei UI", self.font_size.get())
        self.configure(bg=self.bg_color.get())
        self.style.configure("TFrame", background=self.bg_color.get())
        self.style.configure("TLabelframe", background=self.bg_color.get())
        self.style.configure("TLabelframe.Label", font=("Microsoft YaHei UI", self.font_size.get(), "bold"))
        self.style.configure("TLabel", background=self.bg_color.get(), font=font)
        self.style.configure("TButton", font=font, padding=5)
        self.style.configure("TEntry", font=font)
        self.style.configure("TCombobox", font=font)
        self.style.configure("Treeview", font=font, rowheight=max(25, self.font_size.get() + 16))
        self.style.configure("Treeview.Heading", font=("Microsoft YaHei UI", self.font_size.get(), "bold"))

    def _build_widgets(self) -> None:
        header = ttk.Frame(self, padding=12)
        header.pack(fill="x")
        ttk.Label(
            header,
            text="学生宿舍管理系统",
            font=("Microsoft YaHei UI", 22, "bold"),
            foreground="#0f5ea8",
        ).pack(side="left")
        ttk.Label(header, text=" 管理宿舍分配 · 查询空余床位 · CSV保存 · 导出住宿名单").pack(
            side="left", padx=16
        )

        toolbar = ttk.Frame(self, padding=(12, 0, 12, 8))
        toolbar.pack(fill="x")
        ttk.Label(toolbar, text="字体大小").pack(side="left")
        ttk.Scale(toolbar, from_=9, to=16, variable=self.font_size, command=lambda _e: self._apply_style()).pack(
            side="left", padx=8
        )
        ttk.Label(toolbar, text="背景颜色").pack(side="left", padx=(18, 0))
        for name, color in [("浅蓝", "#eef6ff"), ("浅绿", "#effaf2"), ("米色", "#fff7e8"), ("浅灰", "#f4f4f4")]:
            ttk.Button(toolbar, text=name, command=lambda c=color: self.change_bg(c)).pack(side="left", padx=3)
        ttk.Button(toolbar, text="导出住宿名单", command=self.export_roster).pack(side="right", padx=4)
        ttk.Button(toolbar, text="保存到CSV", command=self.save_data).pack(side="right", padx=4)

        body = ttk.Frame(self, padding=12)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        form = ttk.LabelFrame(body, text="宿舍分配", padding=12)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        self._build_form(form)

        notebook = ttk.Notebook(body)
        notebook.grid(row=0, column=1, sticky="nsew")
        roster_tab = ttk.Frame(notebook, padding=8)
        vacancy_tab = ttk.Frame(notebook, padding=8)
        notebook.add(roster_tab, text="住宿名单")
        notebook.add(vacancy_tab, text="空余床位查询")
        self._build_roster_tab(roster_tab)
        self._build_vacancy_tab(vacancy_tab)

        status = ttk.Frame(self, padding=(12, 0, 12, 10))
        status.pack(fill="x")
        self.status_text = tk.StringVar(value="就绪")
        ttk.Label(status, textvariable=self.status_text, foreground="#555").pack(side="left")

    def _build_form(self, parent: ttk.Frame) -> None:
        fields = [
            ("building", "楼号", DEFAULT_BUILDINGS),
            ("room", "房间号", DEFAULT_ROOMS),
            ("bed", "床位", DEFAULT_BEDS),
            ("student_id", "学号", None),
            ("name", "姓名", None),
            ("gender", "性别", ("男", "女")),
            ("major", "专业", None),
            ("phone", "电话", None),
        ]
        for row, (key, label, values) in enumerate(fields):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            self.entries[key] = var
            if values:
                combo = ttk.Combobox(parent, textvariable=var, values=list(values), width=22)
                combo.grid(row=row, column=1, sticky="ew", pady=5)
                combo.current(0)
            else:
                ttk.Entry(parent, textvariable=var, width=24).grid(row=row, column=1, sticky="ew", pady=5)
        ttk.Button(parent, text="分配/更新床位", command=self.submit_assignment).grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(16, 5)
        )
        ttk.Button(parent, text="删除当前床位记录", command=self.delete_assignment).grid(
            row=10, column=0, columnspan=2, sticky="ew", pady=5
        )
        ttk.Button(parent, text="清空输入", command=self.clear_form).grid(
            row=11, column=0, columnspan=2, sticky="ew", pady=5
        )

    def _build_roster_tab(self, parent: ttk.Frame) -> None:
        search_bar = ttk.Frame(parent)
        search_bar.pack(fill="x", pady=(0, 8))
        self.search_keyword = tk.StringVar()
        ttk.Label(search_bar, text="关键词").pack(side="left")
        ttk.Entry(search_bar, textvariable=self.search_keyword, width=28).pack(side="left", padx=6)
        ttk.Button(search_bar, text="搜索", command=self.refresh_roster).pack(side="left")
        ttk.Button(search_bar, text="显示全部", command=self.show_all_roster).pack(side="left", padx=5)

        columns = ("place", "student_id", "name", "gender", "major", "phone")
        self.roster_tree = ttk.Treeview(parent, columns=columns, show="headings")
        headings = ["宿舍位置", "学号", "姓名", "性别", "专业", "电话"]
        widths = [160, 120, 100, 70, 140, 130]
        for column, heading, width in zip(columns, headings, widths):
            self.roster_tree.heading(column, text=heading)
            self.roster_tree.column(column, width=width, anchor="center")
        self.roster_tree.pack(fill="both", expand=True, side="left")
        self.roster_tree.bind("<<TreeviewSelect>>", self.on_roster_select)
        roster_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.roster_tree.yview)
        roster_scrollbar.pack(side="right", fill="y")
        self.roster_tree.configure(yscrollcommand=roster_scrollbar.set)

    def _build_vacancy_tab(self, parent: ttk.Frame) -> None:
        query = ttk.Frame(parent)
        query.pack(fill="x", pady=(0, 8))
        self.vacancy_building = tk.StringVar(value="全部")
        self.vacancy_room = tk.StringVar()
        ttk.Label(query, text="楼号").pack(side="left")
        ttk.Combobox(
            query,
            textvariable=self.vacancy_building,
            values=["全部", *DEFAULT_BUILDINGS],
            width=12,
            state="readonly",
        ).pack(side="left", padx=6)
        ttk.Label(query, text="房间关键字").pack(side="left", padx=(12, 0))
        ttk.Entry(query, textvariable=self.vacancy_room, width=18).pack(side="left", padx=6)
        ttk.Button(query, text="查询空余床位", command=self.refresh_vacancy).pack(side="left")

        columns = ("building", "room", "bed")
        self.vacancy_tree = ttk.Treeview(parent, columns=columns, show="headings")
        for column, heading, width in zip(columns, ["楼号", "房间号", "床位"], [160, 160, 160]):
            self.vacancy_tree.heading(column, text=heading)
            self.vacancy_tree.column(column, width=width, anchor="center")
        self.vacancy_tree.pack(fill="both", expand=True, side="left")
        self.vacancy_tree.bind("<<TreeviewSelect>>", self.on_vacancy_select)
        vacancy_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.vacancy_tree.yview)
        vacancy_scrollbar.pack(side="right", fill="y")
        self.vacancy_tree.configure(yscrollcommand=vacancy_scrollbar.set)

    def change_bg(self, color: str) -> None:
        self.bg_color.set(color)
        self._apply_style()

    def current_assignment(self) -> Assignment:
        return Assignment(**{key: var.get().strip() for key, var in self.entries.items()})

    def submit_assignment(self) -> None:
        try:
            action = self.manager.add_or_update(self.current_assignment())
        except ValueError as error:
            messagebox.showwarning("提示", str(error))
            return
        self.status_text.set(f"{action}成功：{self.current_assignment().place}")
        self.refresh_tables()

    def delete_assignment(self) -> None:
        item = self.current_assignment()
        if self.manager.delete(item.building, item.room, item.bed):
            self.status_text.set(f"已删除：{item.place}")
            self.refresh_tables()
            self.clear_form(keep_place=True)
        else:
            messagebox.showinfo("提示", "当前床位没有住宿记录。")

    def clear_form(self, keep_place: bool = False) -> None:
        for key, var in self.entries.items():
            if keep_place and key in {"building", "room", "bed"}:
                continue
            if key == "gender":
                var.set("男")
            elif key in {"building", "room", "bed"}:
                pass
            else:
                var.set("")

    def refresh_tables(self) -> None:
        self.refresh_roster()
        self.refresh_vacancy()

    def refresh_roster(self) -> None:
        for item in self.roster_tree.get_children():
            self.roster_tree.delete(item)
        for assignment in self.manager.search_students(self.search_keyword.get()):
            self.roster_tree.insert(
                "",
                "end",
                values=(
                    assignment.place,
                    assignment.student_id,
                    assignment.name,
                    assignment.gender,
                    assignment.major,
                    assignment.phone,
                ),
            )
        self.status_text.set(
            f"住宿 {len(self.manager.assignments)} 人，空余床位 {len(self.manager.vacant_beds())} 个。"
        )

    def show_all_roster(self) -> None:
        self.search_keyword.set("")
        self.refresh_roster()

    def refresh_vacancy(self) -> None:
        for item in self.vacancy_tree.get_children():
            self.vacancy_tree.delete(item)
        vacancies = self.manager.vacant_beds(self.vacancy_building.get(), self.vacancy_room.get().strip())
        for vacancy in vacancies:
            self.vacancy_tree.insert("", "end", values=vacancy)

    def on_roster_select(self, _event: tk.Event) -> None:
        selected = self.roster_tree.selection()
        if not selected:
            return
        place, student_id, name, gender, major, phone = self.roster_tree.item(selected[0], "values")
        building, room, bed = place.split("-", 2)
        values = {
            "building": building,
            "room": room,
            "bed": bed,
            "student_id": student_id,
            "name": name,
            "gender": gender,
            "major": major,
            "phone": phone,
        }
        for key, value in values.items():
            self.entries[key].set(value)

    def on_vacancy_select(self, _event: tk.Event) -> None:
        selected = self.vacancy_tree.selection()
        if not selected:
            return
        building, room, bed = self.vacancy_tree.item(selected[0], "values")
        self.entries["building"].set(building)
        self.entries["room"].set(room)
        self.entries["bed"].set(bed)
        self.status_text.set(f"已选择空床位：{building}-{room}-{bed}")

    def save_data(self) -> None:
        self.manager.save()
        messagebox.showinfo("保存成功", f"数据已保存到：{self.manager.data_file.resolve()}")

    def export_roster(self) -> None:
        target = filedialog.asksaveasfilename(
            title="导出住宿名单",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv")],
            initialfile="住宿名单.csv",
        )
        if not target:
            return
        self.manager.export_roster(Path(target))
        messagebox.showinfo("导出成功", f"住宿名单已导出到：{target}")


def run_self_test() -> None:
    """不启动 GUI 的基础功能测试，便于无图形环境检查。"""
    with tempfile.TemporaryDirectory() as temp_dir:
        data_file = Path(temp_dir) / "dormitory_data.csv"
        export_file = Path(temp_dir) / "roster.csv"
        manager = DormitoryManager(data_file=data_file, buildings=["A楼"], rooms=["101"], beds=["1床", "2床"])
        manager.add_or_update(Assignment("A楼", "101", "1床", "2026001", "张三", "男", "计算机", "13800000000"))
        assert len(manager.search_students("张三")) == 1
        assert manager.vacant_beds() == [("A楼", "101", "2床")]
        manager.export_roster(export_file)
        assert "张三" in export_file.read_text(encoding="utf-8-sig")
        reloaded = DormitoryManager(data_file=data_file, buildings=["A楼"], rooms=["101"], beds=["1床", "2床"])
        assert len(reloaded.assignments) == 1
        assert reloaded.delete("A楼", "101", "1床") is True
        assert len(reloaded.vacant_beds()) == 2
    print("self-test passed")


def main() -> None:
    parser = argparse.ArgumentParser(description="第47题：学生宿舍管理系统")
    parser.add_argument("--self-test", action="store_true", help="运行无界面自检")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    app = DormitoryApp(DormitoryManager())
    app.mainloop()


if __name__ == "__main__":
    main()
