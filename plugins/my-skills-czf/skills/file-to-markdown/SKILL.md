---
name: file-to-markdown
description: "Use when converting PDF, Word, Excel, PowerPoint, images, audio, HTML, CSV, JSON, XML, ZIP, EPUB, or YouTube content into Markdown for LLM processing or text analysis."
---

# 文件转 Markdown

## Workflow

1. 先确认输入来源、文件类型、输出位置和是否需要 OCR、语音转录、图片描述、插件或 Azure Document Intelligence。
2. 检查 Python 是否为 3.10+，并检查 `markitdown` 是否可用。缺少依赖时，优先建议在虚拟环境中安装：
   - 全功能：`pip install "markitdown[all]"`
   - 按需安装：`pip install "markitdown[pdf,docx,pptx]"`
3. 对本地可信文件执行转换。简单转换优先使用 CLI：
   - 输出到终端：`markitdown <input>`
   - 输出到文件：`markitdown <input> -o <output.md>`
   - 只有确实需要插件时才加 `--use-plugins`，并先用 `markitdown --list-plugins` 检查插件。
4. 需要程序化处理、批量转换或自定义输出时使用 Python API：

   ```python
   from markitdown import MarkItDown

   converter = MarkItDown(enable_plugins=False)
   result = converter.convert(input_path)
   markdown = result.text_content
   ```

   需要插件时显式设置 `enable_plugins=True`；需要图片描述时传入已配置的 LLM client 和模型；需要 Azure 文档智能时传入 endpoint。
5. 根据输入类型选择依赖和检查结果：
   - 文档：PDF、DOCX、PPTX、XLSX/XLS
   - 图片：常见图片格式，OCR 或图片描述可能需要额外依赖或模型
   - 音频：WAV、MP3，语音转录需要对应可选依赖
   - 网页与文本：HTML、CSV、JSON、XML
   - 容器与电子书：ZIP、EPUB；YouTube 使用其 URL 和字幕能力
6. 验证输出：确认 Markdown 非空、标题/列表/表格等结构仍可用，必要时检查编码、页码或来源信息。若输出用于 RAG，保留文件名、页码、段落等元数据。
7. 向用户返回 Markdown 内容或输出文件路径，并说明未安装的可选依赖、解析失败的文件和质量限制。

## Constraints

- Markdown 目标是 LLM 处理和文本分析，不承诺面向人类阅读的高保真排版。
- 不要把不受信任的文件直接交给插件或外部服务；处理前确认来源，尤其要防范插件执行、宏内容和敏感数据外泄。
- 大文件可能消耗较多内存。必要时拆分文件、限制批量大小或改用异步处理；不要承诺实时流式转换。
- 不要在 Skill 中写入 API Key、Cookie、Token、私钥或其他凭据；外部 LLM/Azure 能力必须从安全的运行环境读取认证信息。
- 使用 `convert_stream()` 时传入二进制文件对象；不要依赖旧版的文件路径接口假设。

## Output

默认直接返回 Markdown；用户要求保存时写入 UTF-8 编码的 `.md` 文件。转换失败时返回具体文件、错误原因、缺少的依赖和可执行的下一步。
