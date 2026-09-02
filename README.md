# Adam Zheng 的公开笔记

这是 [`ZhongshuZheng.github.io`](https://ZhongshuZheng.github.io/) 的源代码，使用 MkDocs Material 构建，并由 GitHub Actions 自动部署到 GitHub Pages。

## 本地预览

```powershell
D:\SoftWares\miniforge3\python.exe -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt --proxy http://127.0.0.1:7897
.\.venv\Scripts\python.exe -m mkdocs serve
```

浏览器访问 `http://127.0.0.1:8000/` 即可预览。

## 内容结构

- `docs/notes/`：主题式公开笔记
- `docs/blog/posts/`：按时间发布的博客文章
- `mkdocs.yml`：站点导航、主题和插件配置
- `.github/workflows/pages.yml`：GitHub Pages 自动部署流程

提交并推送到 `main` 分支后，GitHub Actions 会自动构建和部署站点。

