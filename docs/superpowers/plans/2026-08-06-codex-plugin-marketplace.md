# Codex Plugin Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有个人 Skill 仓库改造成支持 GitHub 与本地安装的 Codex marketplace，同时保留其他 Agent 的传统安装方式。

**Architecture:** 仓库根目录作为 marketplace 根目录，`plugins/my-skills-czf/` 作为唯一 Codex 插件根目录，插件内的 `skills/` 是唯一 Skill 源码目录。仓库自带无第三方依赖的 Skill 与插件清单校验，Codex 官方 `plugin-creator` 校验作为交付前的额外质量门禁。

**Tech Stack:** JSON、Markdown、Python 3.12 标准库、PowerShell、Bash、GitHub Actions、Codex plugin manifest

---

## 文件结构

- 创建 `.agents/plugins/marketplace.json`：声明仓库 marketplace 和可安装插件。
- 创建 `plugins/my-skills-czf/.codex-plugin/plugin.json`：声明插件元数据与 Skill 路径。
- 移动 `skills/*` 到 `plugins/my-skills-czf/skills/*`：形成唯一 Skill 源码目录。
- 修改 `scripts/new_skill.py`：在插件内创建新 Skill。
- 修改 `scripts/validate_skills.py`：从插件内发现并校验 Skill。
- 创建 `scripts/validate_plugin.py`：无第三方依赖地校验 marketplace 与插件清单的仓库约束。
- 修改 `scripts/install.ps1` 和 `scripts/install.sh`：从插件内安装 Skill。
- 修改 `.github/workflows/validate.yml`：在 CI 中运行两类校验。
- 修改 `AGENTS.md`：更新 Skill 创作路径约束。
- 修改 `README.md`：记录 Codex GitHub、本地和传统安装流程。

### Task 1: 迁移唯一 Skill 源目录

**Files:**
- Move: `skills/auto-create-skill/` -> `plugins/my-skills-czf/skills/auto-create-skill/`
- Move: `skills/code-flow-lifecycle-walkthrough/` -> `plugins/my-skills-czf/skills/code-flow-lifecycle-walkthrough/`
- Move: `skills/doc-cv-description/` -> `plugins/my-skills-czf/skills/doc-cv-description/`
- Delete: `skills/.gitkeep`

- [ ] **Step 1: 记录迁移前状态**

Run: `git status --short`

Expected: 只显示用户已有的 `skills/doc-cv-description/SKILL.md` 修改和计划文档；记录该修改供迁移后比对。

- [ ] **Step 2: 创建插件 Skill 目录并移动三个 Skill**

使用同一文件系统内的目录移动，目标固定为：

```text
plugins/my-skills-czf/skills/auto-create-skill
plugins/my-skills-czf/skills/code-flow-lifecycle-walkthrough
plugins/my-skills-czf/skills/doc-cv-description
```

移动前确认源目录存在、目标目录不存在；移动后删除空的根级 `skills/`。不得改写三个 `SKILL.md` 或 `agents/openai.yaml` 的内容。

- [ ] **Step 3: 验证用户修改随目录完整迁移**

Run: `git diff -- plugins/my-skills-czf/skills/doc-cv-description/SKILL.md`

Expected: 内容差异与迁移前用户修改一致，没有丢失或回退。

### Task 2: 创建插件和 Marketplace 清单

**Files:**
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/my-skills-czf/.codex-plugin/plugin.json`

- [ ] **Step 1: 创建 marketplace 清单**

写入以下完整 JSON：

```json
{
  "name": "my-skills-czf",
  "interface": {
    "displayName": "My Skills CZF"
  },
  "plugins": [
    {
      "name": "my-skills-czf",
      "source": {
        "source": "local",
        "path": "./plugins/my-skills-czf"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 2: 创建插件清单**

写入以下完整 JSON：

```json
{
  "name": "my-skills-czf",
  "version": "0.1.0",
  "description": "Reusable Codex skills for code walkthroughs, technical project summaries, and personal skill authoring.",
  "author": {
    "name": "thvvvchen",
    "url": "https://github.com/thvvvchen"
  },
  "homepage": "https://github.com/thvvvchen/my-skills",
  "repository": "https://github.com/thvvvchen/my-skills",
  "keywords": ["codex", "skills", "productivity"],
  "skills": "./skills/",
  "interface": {
    "displayName": "My Skills CZF",
    "shortDescription": "Reusable skills for code analysis and technical writing.",
    "longDescription": "A personal collection of reusable Codex skills for tracing real code flows, preparing technical project and interview materials, and maintaining new skills in the repository.",
    "developerName": "thvvvchen",
    "category": "Productivity",
    "capabilities": ["Code analysis", "Technical writing", "Skill authoring"],
    "defaultPrompt": [
      "Trace this feature's real code flow and lifecycle.",
      "Turn this implementation into resume and interview material.",
      "Add this reusable workflow to my personal skill repository."
    ]
  }
}
```

- [ ] **Step 3: 验证 JSON 可解析且路径存在**

Run: `python -m json.tool .agents/plugins/marketplace.json`

Expected: exit 0，并输出格式化 JSON。

Run: `python -m json.tool plugins/my-skills-czf/.codex-plugin/plugin.json`

Expected: exit 0，并输出格式化 JSON。

### Task 3: 适配仓库脚本并增加插件校验

**Files:**
- Modify: `scripts/new_skill.py`
- Modify: `scripts/validate_skills.py`
- Modify: `scripts/install.ps1`
- Modify: `scripts/install.sh`
- Create: `scripts/validate_plugin.py`

- [ ] **Step 1: 先修改发现路径并确认旧实现失败**

将四个现有脚本中的根级 `skills` 路径统一替换为 `plugins/my-skills-czf/skills`。Python 使用：

```python
def skills_root() -> Path:
    return repository_root() / "plugins" / "my-skills-czf" / "skills"
```

`new_skill.py` 使用 `skills_root() / name`，`validate_skills.py` 使用 `skills_root()`；PowerShell 使用：

```powershell
$skillsRoot = Join-Path $repoRoot 'plugins\my-skills-czf\skills'
```

Bash 使用：

```bash
skills_root="$repo_root/plugins/my-skills-czf/skills"
```

Run: `python scripts/validate_skills.py`

Expected: 若 Task 1 尚未迁移则失败或找不到 Skill；Task 1 完成后输出三个 `PASS`。

- [ ] **Step 2: 添加仓库内插件校验器**

实现 `scripts/validate_plugin.py`，仅使用 Python 标准库，并执行以下确定性检查：

```python
PLUGIN_NAME = "my-skills-czf"
PLUGIN_ROOT = repository_root() / "plugins" / PLUGIN_NAME
MARKETPLACE_PATH = repository_root() / ".agents" / "plugins" / "marketplace.json"
SEMVER_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$")
INSTALL_POLICIES = {"NOT_AVAILABLE", "AVAILABLE", "INSTALLED_BY_DEFAULT"}
AUTH_POLICIES = {"ON_INSTALL", "ON_USE"}
```

校验器必须：解析两个 JSON 对象；验证插件名、严格 semver、描述、作者名、`skills` 路径和五个必需 interface 字段；验证 capabilities 为非空字符串数组；验证 defaultPrompt 为 1 至 3 个非空字符串且每项不超过 128 字符；验证 marketplace 同名条目唯一、source 为 local、相对路径精确为 `./plugins/my-skills-czf`、安装和认证策略在允许集合内、category 非空；最后确认路径解析后仍位于仓库内且 `plugin.json` 与 `skills/` 均存在。

成功输出：

```text
Validated plugin my-skills-czf and marketplace my-skills-czf.
```

失败时逐条输出 `FAIL <message>` 并返回 1。

- [ ] **Step 3: 运行仓库校验**

Run: `python scripts/validate_skills.py`

Expected: `Validated 3 skill(s).`

Run: `python scripts/validate_plugin.py`

Expected: `Validated plugin my-skills-czf and marketplace my-skills-czf.`

- [ ] **Step 4: 非破坏性检查 PowerShell 安装脚本**

Run: `powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent codex -WhatIf`

Expected: 发现三个 Skill，并只输出模拟安装动作，不移除或写入已有 Codex Skill。

- [ ] **Step 5: 检查 Bash 语法**

Run: `bash -n scripts/install.sh`

Expected: exit 0。若当前 Windows 环境没有 Bash，明确记录未执行，不以替代命令伪造通过。

### Task 4: 更新仓库规则、文档与 CI

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `.github/workflows/validate.yml`

- [ ] **Step 1: 更新 AGENTS.md 的唯一源码约束**

将所有 `skills/<skill-name>/` 改为 `plugins/my-skills-czf/skills/<skill-name>/`，并新增规则：

```markdown
- Treat `plugins/my-skills-czf/skills/` as the only source of installable skills.
- Keep `.agents/plugins/marketplace.json` and `plugins/my-skills-czf/.codex-plugin/plugin.json` valid when changing plugin metadata or layout.
```

- [ ] **Step 2: 重写 README 安装章节**

README 必须包含：仓库结构；创建与校验 Skill；从 GitHub 添加 marketplace 并安装插件；从本地仓库添加 marketplace 并安装插件；Windows 与 macOS/Linux 的传统安装命令；隐私约束。Codex 命令采用：

```powershell
codex plugin marketplace add https://github.com/thvvvchen/my-skills.git
codex plugin add my-skills-czf@my-skills-czf
```

本地 marketplace 命令采用：

```powershell
codex plugin marketplace add C:\path\to\my-skills-czf
codex plugin add my-skills-czf@my-skills-czf
```

README 将 `C:\\path\\to\\my-skills-czf` 明确标注为需由安装者替换的示例参数，不写入开发者机器的真实绝对路径。

- [ ] **Step 3: 扩展 GitHub Actions**

保留 Python 3.12，并将校验步骤改为：

```yaml
      - run: python scripts/validate_skills.py
      - run: python scripts/validate_plugin.py
```

- [ ] **Step 4: 扫描旧路径引用**

Run: `rg -n '(repository_root\(\) / "skills"|repoRoot.*skills|repo_root/skills|skills/<skill-name>)' --glob '!docs/superpowers/**'`

Expected: 无指向旧根级 Skill 源目录的有效逻辑或创作规则。

### Task 5: 官方校验与最终质量门禁

**Files:**
- Verify: `plugins/my-skills-czf/`
- Verify: `.agents/plugins/marketplace.json`
- Verify: all modified repository files

- [ ] **Step 1: 运行 Codex 官方插件校验器**

Run: `python <plugin-creator-root>/scripts/validate_plugin.py plugins/my-skills-czf`

Expected: `Plugin validation passed`。此命令依赖本机 `plugin-creator` skill 环境，不写入仓库。

- [ ] **Step 2: 运行完整仓库门禁**

Run: `python scripts/validate_skills.py`

Expected: `Validated 3 skill(s).`

Run: `python scripts/validate_plugin.py`

Expected: `Validated plugin my-skills-czf and marketplace my-skills-czf.`

Run: `git diff --check`

Expected: 无 whitespace error。

- [ ] **Step 3: 审核最终变更范围**

Run: `git status --short`

Expected: 只包含本计划的迁移与改造文件，以及用户原有 `doc-cv-description` 内容修改在新路径下的对应状态。

Run: `git diff --stat`

Expected: 三个 Skill 表现为目录迁移，脚本、文档和 CI 为定向修改，不包含凭据、缓存或生成物。

- [ ] **Step 4: 报告安装入口与新任务验证要求**

交付说明必须给出 GitHub 和本地安装入口、各校验命令结果，并提示安装或更新插件后新建 Codex 任务，以载入新的 Skill 列表。
