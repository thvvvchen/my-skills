# 数据库设计通用规范

## 1. 表设计规范

### 1.1 表分类

| 分类 | 说明 | 是否豁免标准规范 |
|-----|------|--------------|
| **定义表** | 静态配置数据 | 否 |
| **实例表** | 核心业务数据 | 否 |
| **关系表** | 多对多关联 | 否 |
| **日志表** | 仅 INSERT，不可修改 | 是（豁免） |

> 不满足规范的例外情况，必须经过评审后才能执行。

### 1.2 字段分组顺序

设计表时，字段按以下顺序分组排列：
1. **非功能属性** — 标准基础字段（id、创建/更新时间、版本号、逻辑删除）
2. **关键属性** — 业务主键、外键、核心状态字段
3. **主要属性** — 核心业务数据字段
4. **扩展属性** — `ctrl_json`、`ext_json` 等扩展字段
5. **附加属性** — 备注、冗余统计等字段

### 1.3 标准非功能字段【强制】

以下字段必须放在表头，字段名、类型、默认值、顺序均不可变更：

| # | 字段名 | 类型 | 默认值 | 含义 |
|---|-------|------|--------|------|
| 1 | `id` | `bigint unsigned PRIMARY KEY AUTO_INCREMENT` | 自增 | 主键标识 |
| 2 | `create_user` | `varchar(64) NOT NULL` | `''` | 创建记录调用方标识 |
| 3 | `create_time` | `datetime NOT NULL` | `CURRENT_TIMESTAMP` | 创建记录时间 |
| 4 | `update_user` | `varchar(64) NOT NULL` | `''` | 更新记录调用方标识 |
| 5 | `update_time` | `datetime NOT NULL` | `CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP` | 更新记录时间 |
| 6 | `version` | `int unsigned NOT NULL` | `0` | 乐观锁标记（每次编辑 +1） |
| 7 | `is_del` | `tinyint unsigned NOT NULL` | `0` | 逻辑删除，0=未删除，1=已删除 |

### 1.4 其他设计规范

- **[强制]** 表名使用 `snake_case`
- **[强制]** 字符集统一 `utf8mb4`，排序规则 `utf8mb4_general_ci`
- **[强制]** 存储引擎使用 `InnoDB`
- **[强制]** 每个字段必须有 `COMMENT`
- **[推荐]** 预留扩展字段 `ctrl_json`（varchar(512)）和 `ext_json`（varchar(2048)）

### 1.5 DDL 示例

```sql
CREATE TABLE `example` (
    `id`          bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键',
    `create_user` varchar(64)  NOT NULL DEFAULT ''    COMMENT '创建记录调用方标识',
    `create_time` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建记录时间',
    `update_user` varchar(64)  NOT NULL DEFAULT ''    COMMENT '更新记录调用方标识',
    `update_time` datetime     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新记录时间',
    `version`     int unsigned NOT NULL DEFAULT 0     COMMENT '乐观锁标记',
    `is_del`      tinyint unsigned NOT NULL DEFAULT 0 COMMENT '逻辑删除，0未删除，1已删除',
    -- 业务字段
    `biz_id`      varchar(128) NOT NULL               COMMENT '业务ID',
    `ctrl_json`   varchar(512) NOT NULL DEFAULT ''    COMMENT '控制字段',
    `ext_json`    varchar(2048) NOT NULL DEFAULT ''   COMMENT '扩展字段',
    PRIMARY KEY (`id`),
    KEY `idx_biz_id` (`biz_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='示例表';
```

## 2. DDL 变更规范

- **[强制]** 禁止在生产环境执行 `DROP TABLE`、`DROP COLUMN`、`RENAME COLUMN` 等破坏性操作
- **[推荐]** DDL 变更先在测试环境验证，确认无锁表风险后上线
- **[推荐]** 新增列使用 `AFTER` 指定位置，保持字段分组顺序

## 3. SQL 编写规范

### 3.1 安全规范

- **[强制]** 严禁直接拼接 SQL，必须使用参数化查询或 ORM 链式 API
- **[强制]** 严禁在 SQL 中硬编码敏感信息（密码、密钥、Token）

### 3.2 性能规范

- **[强制]** 查询必须有合适的索引，严禁全表扫描
- **[强制]** 禁止 `SELECT *`，必须明确指定需要的字段
- **[推荐]** 复杂查询先在测试环境 `EXPLAIN` 分析执行计划
- **[推荐]** 分页查询使用覆盖索引优化
- **[推荐]** 大表查询必须有 `LIMIT`

### 3.3 写操作规范

- **[推荐]** 更新操作使用 `version` 字段实现乐观锁
- **[推荐]** 删除操作使用逻辑删除（`is_del = 1`），不使用物理删除

## 4. 索引设计规范

### 4.1 索引类型与使用场景

| 索引类型 | 使用场景 |
|---------|---------|
| 主键索引 | `id` 字段，自动创建 |
| 唯一索引 | 业务唯一约束字段（单字段） |
| 唯一联合索引 | 多字段组合的唯一约束 |
| 普通索引 | 高频查询条件字段、外键字段（单字段） |
| 联合索引 | 多字段组合查询，遵循最左前缀原则 |

### 4.2 索引命名规范【强制】

| 索引类型 | 命名规范 | 示例 |
|---------|---------|------|
| 主键索引 | 无需命名（MySQL 自动为 `PRIMARY`） | - |
| 唯一索引（单字段） | `uk_{字段名}` | `uk_order_no` |
| 唯一索引（多字段） | `uk_{字段1}_{字段2}` | `uk_user_id_order_no` |
| 普通索引（单字段） | `idx_{字段名}` | `idx_biz_id` |
| 联合索引（多字段） | `idx_{字段1}_{字段2}` | `idx_user_id_status` |

- **[强制]** 索引名必须使用小写字母、数字和下划线，禁止大写
- **[强制]** 联合索引按字段顺序命名，字段名之间用下划线分隔

### 4.3 索引创建规范

- **[强制]** 禁止在频繁更新的字段上单独建索引（如 `update_time`）
- **[强制]** `is_del` 字段不单独建索引，应与业务字段组成联合索引
- **[强制]** 联合索引遵循最左前缀原则，高选择性字段放前面
- **[强制]** 禁止在 `TEXT`/`BLOB` 类型字段上直接建索引
- **[推荐]** 字符串字段建索引时评估前缀索引（如 `INDEX idx_name(name(20))`）
- **[推荐]** 区分度低的字段（如状态、性别、布尔值）不单独建索引
- **[推荐]** 单表索引数量不超过 5 个
- **[推荐]** 联合索引字段数不超过 3 个

### 4.4 索引禁忌【强制】

- **[强制]** 禁止冗余索引（如已有 `idx_a_b`，不再单独建 `idx_a`）
- **[强制]** 禁止重复索引（同一组字段建立多个索引）
- **[强制]** 禁止在索引列上使用函数或表达式（会导致索引失效）

### 4.5 索引示例

```sql
-- ✅ 正确示例
PRIMARY KEY (`id`),
UNIQUE KEY `uk_order_no` (`order_no`),
UNIQUE KEY `uk_user_id_biz_type` (`user_id`, `biz_type`),
KEY `idx_biz_id` (`biz_id`),
KEY `idx_user_id_status` (`user_id`, `status`, `is_del`)

-- ❌ 错误示例
KEY `idx_update_time` (`update_time`),    -- 频繁更新字段，禁止单独建索引
KEY `idx_is_del` (`is_del`),               -- 区分度过低，禁止单独建索引
KEY `IDX_BIZ_ID` (`biz_id`),               -- 禁止大写命名
KEY `idx_user_id` (`user_id`),             -- 冗余索引，已有 idx_user_id_status
```

### 4.6 索引分析

- **[推荐]** 为核心查询 SQL 附上 `EXPLAIN` 分析结果
- **[推荐]** 关注 `type` 列，避免 `ALL`（全表扫描）和 `index`（全索引扫描）
- **[推荐]** 关注 `Extra` 列，避免 `Using filesort` 和 `Using temporary`

## 5. 数据量评估

在方案中需提供以下评估：

| 评估项 | 说明 |
|-------|------|
| 初始数据量 | 上线时的预估行数 |
| 增长速度 | 每日/每月新增行数 |
| 1年/3年数据量 | 是否需要归档或分表 |
| 单行平均大小 | 估算总存储空间 |
| 是否需要分表 | 超过 500w 行建议评估分表策略 |
