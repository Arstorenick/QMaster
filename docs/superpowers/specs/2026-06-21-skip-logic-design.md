# 跳转模式设计

## 概述

在问卷编辑器中新增"跳转模式"，类似现有的评分模式。开启后，单选题/下拉题/图片单选题的每个选项可设置跳转规则（跳到某题或结束问卷）。

## 存储

- `Survey.skip_enabled`：BooleanField，默认 False
- `Question.config.skip_rules`：`{ option_id: target_question_id | null | -1 }`
  - `null` / 不设置 = 默认下一题
  - 正整数 = 目标题目 ID
  - `-1` = 结束问卷

## 编辑器

- 模式栏新增"跳转模式"Tab，与正常/分值互斥
- 跳转模式下题型工具栏仅显示单选、下拉、图片单选
- 每选项下方显示"跳转到 [▼]"下拉，选项为后续题目列表 + "结束问卷"

## 答题端

- 翻页时根据当前页跳转规则计算下一页
- 兼容分页题（page_break）
- 不改变提交逻辑

## 后端

- `Question.config` 已是 JSONField，无需数据库迁移
- `Survey.skip_enabled` 需新增字段 + 迁移
