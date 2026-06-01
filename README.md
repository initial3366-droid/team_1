# 第47题：学生宿舍管理系统

使用 Python 标准库完成的 Tkinter 图形界面程序，围绕题目要求实现：

- 管理宿舍分配（楼号、房间号、床位）
- 查询空余床位
- 数据保存至 CSV 文件
- 支持导出住宿名单

## 运行方法

```bash
python dormitory_management_system.py
```

## 无界面功能检查

```bash
python dormitory_management_system.py --self-test
```

## 特色创新

- 支持住宿名单关键词搜索。
- 支持点击住宿名单自动回填表单，便于修改或删除。
- 支持按楼号、房间关键字筛选空余床位。
- 支持调整字体大小和切换背景颜色。
- 仅使用 Python 标准库，便于课程环境直接运行。


## 样例数据和实物图

仓库已提供 `dormitory_data.csv` 样例住宿数据，直接运行程序即可看到住宿名单。

实物预览图位于 `docs/dormitory_system_preview.svg`，可用浏览器打开查看界面效果。
