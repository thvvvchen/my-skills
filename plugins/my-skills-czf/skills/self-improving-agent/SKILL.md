---
name: self-improving-agent
description: "Use when a skill or workflow produces reusable lessons, recurring errors, or user feedback that should be captured and applied to future work."
---

# Self-Improving Agent

把一次任务中的可靠经验沉淀为可验证、可回滚的改进。只根据证据更新，不把单次偶然现象当成通用规则。

## 闭环

1. **记录经历**：保存技能、任务、结果、关键输入、错误、根因、措施和用户反馈。成功、部分成功和失败都记录。
2. **抽象模式**：提炼一句可迁移规则，说明它解决的问题、适用条件、目标 Skill 和置信度；保留原始经历作为依据。
3. **纠正错误**：先确认是指导错误、执行偏差还是环境问题；只有确认指导错误，才添加带日期、原因和来源的 correction 标记。
4. **验证应用**：用相似但独立的场景验证改进。验证失败就撤回或降低置信度，不叠加未经验证的规则。

## 记忆边界

- **语义记忆**：跨任务复用的模式、约束和置信度。
- **情景记忆**：带时间和上下文的具体经历，便于追溯。
- **工作记忆**：当前任务、待验证假设和最近错误；任务结束后清理临时内容。

建议字段：`id`、`source`、`created`、`confidence`、`applications`、`pattern`、`problem`、`solution`、`target_skills`。

## 更新规则

- 新模式至少有一个明确证据来源；重复出现或被独立场景验证后再提高置信度。
- 修改 Skill 前先读取现状，保留有效约束，用 evolution/correction 标记追踪变更。
- 不因一次低质量结果批量改写多个 Skill；先定位受影响的单一规则。
- 不记录 Cookie、Token、密码、私钥、完整日志或其他敏感数据。
- 不自动提交、推送或修改生产配置；涉及外部变更时先请求用户确认。

## 最小记录模板

```yaml
skill: <skill-name>
task: <what was attempted>
outcome: success | partial | failure
evidence:
  worked: []
  failed: []
root_cause: <if known>
lesson: <reusable rule>
source: user_feedback | implementation_review | retrospective
confidence: 0.0
next_validation: <independent scenario>
```

完成改进时报告：改了什么、证据来自哪里、验证是否通过，以及尚未验证的风险。
