# Word 笔记发布工作流

这套流程将 Word 作为原稿，将 Markdown 和图片作为 MkDocs 的发布内容。转换工具只负责可重复的机械工作，语义层级、图注和文字表达在发布前快速人工确认。

## 1. 保存原稿

把 `.docx` 文件放入 `src_doc/<分类>/`。`src_doc/` 已被 Git 忽略，不会随网站源码公开。

Word 原稿建议使用内置样式：

- 文档名称使用“标题”样式。
- 一级章节使用“标题 1”，下级章节依次使用“标题 2”和“标题 3”。
- 使用 Word 自带的项目符号或编号列表。
- 图片采用嵌入型排列，并在下一行写清图注。
- 不使用连续空行、空格、文本框或浮动图片控制版面。

## 2. 安装转换依赖

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-tools.txt --proxy http://127.0.0.1:7897
```

## 3. 转换 Word

```powershell
.\.venv\Scripts\python.exe tools\docx_to_markdown.py `
  "src_doc\杂项知识\中世纪盔甲.docx" `
  "docs\notes\misc\medieval-armor\index.md"
```

转换器会：

- 按 Word 中的实际顺序读取段落、表格和图片。
- 将 Word 标题与列表样式映射为 Markdown。
- 保留加粗、斜体和超链接。
- 将图片提取到文章旁边的 `images/` 目录。
- 生成适配 Material for MkDocs 的图片容器。
- 输出转换统计与需要人工检查的警告。

如果目标 Markdown 已存在，工具默认拒绝覆盖。确认需要重新生成时添加 `--force`。

## 4. 快速人工检查

- 每篇文章只有一个一级标题。
- 标题层级连续，不依赖字体大小或空行表达结构。
- 相似条目改为列表或表格。
- 每张图片都有准确的替代文本和图注。
- 删除多余日期、导出标记和空段落。
- 核对链接、专有名词、年代和图片使用权限。

## 5. 本地验证

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m mkdocs build --strict
.\.venv\Scripts\python.exe -m mkdocs serve
```

访问 `http://127.0.0.1:8000/` 检查桌面和窄屏布局。确认后再提交、推送和部署。
