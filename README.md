# 第28题：词频统计工具

本项目使用 Python 完成“词频统计工具”：读取文本文件，统计单词/词语频率，生成词云图，支持停用词过滤，并把结果保存为 CSV 文件。

## 功能

- 读取 UTF-8 文本文件并统计词频。
- 支持中文与英文文本；安装 `jieba` 后自动使用中文分词。
- 支持停用词过滤，每行一个停用词。
- 统计结果按频率降序导出为 CSV。
- 优先使用 `wordcloud` 库生成 PNG/JPG 词云；如果当前环境未安装该库，会自动生成 SVG 词云图，保证可以直接运行并看到实物图。

## 安装依赖（推荐）

```bash
python -m pip install -r requirements.txt
```

## 运行示例

```bash
python word_frequency_tool.py \
  --input data/sample_text.txt \
  --stopwords data/stopwords.txt \
  --csv output/word_frequency.csv \
  --image output/wordcloud.png
```

如果环境没有安装 `wordcloud`，程序会自动输出 `output/wordcloud.svg`。

## 输出文件

- `output/word_frequency.csv`：词频统计表。
- `output/wordcloud.svg` 或 `output/wordcloud.png`：词云实物图。
