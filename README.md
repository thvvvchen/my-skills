# my-skills-czf

私人 AI Agent Skill 仓库。所有 Skill 只有一份源码，既可作为 Codex 插件从 GitHub 或本地 marketplace 安装，也可通过传统脚本安装到 Claude Code、Codex、Cursor、Kimi Code CLI 和 Trae。

## 目录结构

```text
my-skills-czf/
|-- .agents/
|   `-- plugins/
|       `-- marketplace.json                 # Codex marketplace 清单
|-- plugins/
|   `-- my-skills-czf/
|       |-- .codex-plugin/
|       |   `-- plugin.json                  # Codex 插件清单
|       `-- skills/                          # 唯一的 Skill 源目录
|-- scripts/
|   |-- new_skill.py                         # 创建 Skill
|   |-- validate_skills.py                   # 校验全部 Skill
|   |-- validate_plugin.py                   # 校验插件与 marketplace
|   |-- install.ps1                          # Windows 传统安装脚本
|   `-- install.sh                           # macOS/Linux 传统安装脚本
|-- AGENTS.md                                # 仓库创作约束
`-- README.md
```

## 创建 Skill

在仓库根目录执行：

```powershell
python scripts/new_skill.py my-first-skill --description "Describe what the skill does and exactly when an agent should use it."
```

脚本会创建 `plugins/my-skills-czf/skills/my-first-skill/SKILL.md`。替换其中的 TODO 后，只按实际需要添加 `references/`、`scripts/` 或 `assets/`，不要预先建立空目录。

完成后运行两类校验：

```powershell
python scripts/validate_skills.py
python scripts/validate_plugin.py
```

## 通过 Codex 安装

### GitHub marketplace

先添加 GitHub 仓库，再安装其中的 `my-skills-czf` 插件：

```powershell
codex plugin marketplace add https://github.com/thvvvchen/my-skills.git
codex plugin add my-skills-czf@my-skills-czf
```

### 本地 marketplace

开发或测试本地修改时，将 marketplace source 指向仓库根目录：

```powershell
codex plugin marketplace add C:\path\to\my-skills-czf
codex plugin add my-skills-czf@my-skills-czf
```

`C:\path\to\my-skills-czf` 是示例参数，请替换为安装者本机的仓库路径。安装或更新插件后，新建一个 Codex 任务以加载最新的 Skill 列表。

## 传统跨 Agent 安装

传统脚本从 `plugins/my-skills-czf/skills/` 读取同一份 Skill 源码。Windows：

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
./scripts/install.sh --agent claude
./scripts/install.sh --agent codex
./scripts/install.sh --agent cursor
./scripts/install.sh --agent kimi
./scripts/install.sh --agent trae
./scripts/install.sh --mode copy --force
```

默认安装位置和模式：

| Agent | 用户级目录 | 自动模式 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | 链接 |
| Codex | `~/.codex/skills/` | 链接 |
| Cursor | `~/.cursor/skills/` | 复制 |
| Kimi Code CLI | `~/.kimi/skills/` | 链接 |
| Trae | `~/.trae/skills/` | 链接 |

Cursor 当前不能稳定发现目录链接，因此安装脚本始终对 Cursor 使用复制模式。仓库内容更新后，需要重新执行带 `-Force` 或 `--force` 的安装命令刷新 Cursor 副本；其他 Agent 默认使用链接，会直接读取仓库中的最新内容。

安装脚本只处理唯一 Skill 源目录下包含 `SKILL.md` 的直接子目录。已有同名目标目录时默认停止，只有传入 `-Force` 或 `--force` 才会替换。Kimi 和 Trae 是否能识别 Skill，取决于所安装客户端版本是否支持 Agent Skills 及上述用户级目录。

## 隐私

不要提交 Token、Cookie、令牌、私钥、生产环境配置或个人隐私数据。需要认证信息的 Skill 应从环境变量、本机凭据存储或对应 Agent 的安全配置中读取，不得将真实凭据写入 Skill、脚本或插件清单。
