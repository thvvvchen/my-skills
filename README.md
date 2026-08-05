# my-skills-czf

私人 AI Agent Skill 仓库，使用一份 Skill 源码同时适配 Claude Code、Codex、Cursor、Kimi Code CLI 和 Trae。

## 目录结构

```text
my-skills-czf/
|-- skills/                 # 唯一的 Skill 源目录
|-- scripts/
|   |-- new_skill.py        # 创建 Skill
|   |-- validate_skills.py  # 校验全部 Skill
|   |-- install.ps1         # Windows 安装脚本
|   `-- install.sh          # macOS/Linux 安装脚本
|-- AGENTS.md               # Agent 在仓库内工作的约束
`-- CLAUDE.md               # Claude Code 入口
```

## 创建 Skill

在仓库根目录执行：

```powershell
python scripts/new_skill.py my-first-skill --description "Describe what the skill does and exactly when an agent should use it."
```

然后编辑 `skills/my-first-skill/SKILL.md`。需要详细知识、自动化脚本或输出素材时，再分别创建 `references/`、`scripts/` 或 `assets/`，不要预先建立空目录。

## 校验

```powershell
python scripts/validate_skills.py
```

## 安装

Windows：

```powershell
# 默认安装到全部五个 Agent
powershell -ExecutionPolicy Bypass -File scripts/install.ps1

# 只安装到指定 Agent
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent claude
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent codex
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent cursor
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent kimi
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Agent trae

# 强制使用复制模式；重复安装时显式覆盖
powershell -ExecutionPolicy Bypass -File scripts/install.ps1 -Mode copy -Force
```

macOS/Linux：

```bash
./scripts/install.sh
./scripts/install.sh --agent cursor
./scripts/install.sh --agent kimi
./scripts/install.sh --agent trae
./scripts/install.sh --mode copy --force
```

默认安装位置和模式：

| Agent | 目录 | 自动模式 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/<skill-name>` | 链接 |
| Codex | `~/.codex/skills/<skill-name>` | 链接 |
| Cursor | `~/.cursor/skills/<skill-name>` | 复制 |
| Kimi Code CLI | `~/.kimi/skills/<skill-name>` | 链接 |
| Trae | `~/.trae/skills/<skill-name>` | 链接 |

Cursor 当前不能稳定发现目录链接，因此安装脚本始终对 Cursor 使用复制模式。仓库内容更新后，需要重新执行带 `-Force` 或 `--force` 的安装命令来刷新 Cursor 副本。其他 Agent 默认使用链接，修改仓库后会直接读取最新内容。

安装脚本只处理 `skills/` 下包含 `SKILL.md` 的直接子目录。已有同名目录时默认停止，只有传入 `-Force` 或 `--force` 才会替换。

Kimi 和 Trae 是否能识别 Skill，取决于所安装客户端版本是否支持 Agent Skills 及上述用户级目录。仓库中的 Skill 仍以通用的 `SKILL.md` 作为跨工具兼容层。

## 隐私

不要提交 Token、Cookie、私钥、生产环境配置或个人隐私数据。需要认证信息的 Skill 应从环境变量、本机凭据存储或对应 Agent 的安全配置中读取。

