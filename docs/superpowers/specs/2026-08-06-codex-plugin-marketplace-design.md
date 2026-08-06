# Codex Plugin Marketplace 改造设计

## 目标

将当前个人 Skill 仓库改造为可被 Codex 插件系统识别和安装的 marketplace，同时保留现有 Claude Code、Codex、Cursor、Kimi Code CLI 和 Trae 的手动安装方式。改造后，每个 Skill 只保留一份源码，避免插件目录与传统安装目录之间发生内容漂移。

## 范围

本次改造包含：

- 新增仓库级 Codex marketplace 清单。
- 新增 `my-skills-czf` 插件清单。
- 将现有 Skill 移入插件的 `skills/` 目录。
- 调整 Skill 创建、校验和跨 Agent 安装脚本的源码路径。
- 更新 CI，使其同时校验 Skill 与 Codex 插件结构。
- 更新根目录 README，说明 GitHub、本地 marketplace 和传统脚本三种安装方式。

本次不增加 MCP server、hook、app、认证、图标、截图或其他运行时能力，也不改变现有 Skill 的行为。

## 目录结构

改造后的核心结构为：

```text
my-skills-czf/
|-- .agents/
|   `-- plugins/
|       `-- marketplace.json
|-- plugins/
|   `-- my-skills-czf/
|       |-- .codex-plugin/
|       |   `-- plugin.json
|       `-- skills/
|           |-- auto-create-skill/
|           |-- code-flow-lifecycle-walkthrough/
|           `-- doc-cv-description/
|-- scripts/
|-- docs/
|-- AGENTS.md
`-- README.md
```

仓库根目录是 marketplace 根目录，`plugins/my-skills-czf/` 是唯一插件根目录，`plugins/my-skills-czf/skills/` 是所有 Skill 的唯一源码目录。

## Marketplace 与插件清单

marketplace 名称和插件标识均使用 `my-skills-czf`，插件展示名使用 `My Skills CZF`。marketplace 通过相对路径 `./plugins/my-skills-czf` 引用插件，并设置：

- `policy.installation` 为 `AVAILABLE`。
- `policy.authentication` 为 `ON_INSTALL`。
- `category` 为 `Productivity`。

插件清单使用严格语义化版本，初始版本为 `0.1.0`，并声明 `./skills/` 为 Skill 目录。作者信息使用仓库所有者 `thvvvchen`，仓库与主页指向 `https://github.com/thvvvchen/my-skills`。不声明仓库当前不存在或无法验证的许可证、隐私政策、服务条款和媒体资源。

插件界面元数据只包含插件列表和详情页所需字段，包括展示名、简短说明、详细说明、开发者名称、分类、能力和最多三个起始提示词。所有描述均准确反映当前三个 Skill 的用途。

## 脚本与兼容性

`scripts/new_skill.py` 与 `scripts/validate_skills.py` 的 Skill 根路径改为 `plugins/my-skills-czf/skills/`。Windows 与 macOS/Linux 安装脚本也从该目录发现 Skill，目标 Agent、链接或复制策略、覆盖保护等现有行为保持不变。

`AGENTS.md` 中的创作规则和工作流同步更新为新的唯一源码路径，避免后续 Agent 在仓库根目录重新创建 `skills/`。根目录 `skills/` 在迁移完成后不再作为安装源。

## 安装流程

GitHub 分发流程以仓库 URL 作为 marketplace 来源。用户先将 marketplace 添加到 Codex，再通过 marketplace 名称安装 `my-skills-czf` 插件。

本地开发流程以本仓库根目录作为 marketplace 来源，安装同名插件。插件清单发生变化时，通过版本或 Codex cachebuster 机制重新安装，并在新任务中验证新载入的 Skill。

非 Codex 用户继续运行现有 `install.ps1` 或 `install.sh`，脚本从插件内的唯一 Skill 源目录安装到对应客户端。

README 将提供实际可执行的命令，并明确区分 GitHub marketplace、本地 marketplace 和传统脚本安装，避免用户混用入口。

## 错误处理与安全

- marketplace 清单只引用仓库内存在的插件相对路径。
- 插件清单只声明实际存在的组件，不声明 MCP、app、hook 或媒体文件。
- 创建脚本拒绝重复或非法 Skill 名称的既有规则保持不变。
- 安装脚本继续在目标已存在且未显式传入强制覆盖参数时停止。
- 仓库不包含 Token、Cookie、密钥、生产凭据或本地绝对路径。
- 迁移保留所有现有 Skill 内容和用户未提交修改。

## 验证方案

完成改造后执行以下机械校验：

1. 运行 `python scripts/validate_skills.py`，确认全部 Skill 的目录名、frontmatter 和占位符检查通过。
2. 使用 Codex `plugin-creator` 提供的 `validate_plugin.py` 校验 `plugins/my-skills-czf/`。
3. 解析 `.agents/plugins/marketplace.json`，确认插件名称、策略字段和相对路径正确，目标清单真实存在。
4. 运行安装脚本的 PowerShell `-WhatIf` 路径或等价非破坏性检查，确认脚本能从新目录发现全部 Skill。
5. 更新 GitHub Actions，使提交时自动执行仓库内 Skill 校验和插件清单校验。

## 完成标准

- Codex 能通过本地 marketplace 识别并安装 `my-skills-czf`。
- 仓库布局满足 GitHub marketplace 分发要求。
- 三个现有 Skill 仅在插件目录保留一份，并通过校验。
- 传统跨 Agent 安装脚本仍能发现并安装全部 Skill。
- README、AGENTS.md、脚本和 CI 中不存在指向旧 Skill 根目录的有效说明或逻辑。
- 用户原有的未提交修改得到完整保留。
