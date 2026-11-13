# 成果字段

`prepare-submit` 接收一条成果或 `{"items":[...]}`。新增时提供 `kind` 和 `fields`，编辑时提供条目 `id` 和要修改的 `fields`，例如 `{"id":"条目 UUID","fields":{"venue":"新发表渠道"}}`。预览会把改动合并到现有字段。字段值均为字符串，空字符串表示清空可选字段。

| 类型 | 可用字段 |
| --- | --- |
| 论文 `paper` | `title` 题名、`authors` 作者、`doi` DOI、`url` 论文链接、`year` 年份、`venue` 发表渠道、`abstract` 摘要、`code_url` 代码链接、`data_url` 数据链接 |
| 项目 `project` | `name` 名称、`description` 简介、`role` 本人角色、`contribution` 本人贡献、`project_type` 项目类型、`start_date` 开始日期、`end_date` 结束日期、`progress` 项目进展、`url` 项目链接 |

- 新增论文须提供题名、作者，以及 DOI 或论文链接。DOI 填编号，年份填四位数字。
- 新增项目须提供项目名称、简介和本人角色。日期使用 `YYYY-MM-DD`。
- 编辑档案中的论文时须保留题名。项目库条目须保留项目名称和本人角色，其他档案项目须保留项目名称和简介。缺少必填资料时向导师核实。
- 项目审核通过后，现有合并规则只会补充已有项目的空简介和空角色。改动这些已有值时应告诉导师这一限制。
