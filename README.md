# 创智龙科研资料助手

`sii-long-profile` 是一个本地 Agent Skill，用于查询和维护导师本人的论文与项目。它可以预览改动、保存草稿，并在导师确认后提交审核。

## 1. 安装

在 macOS 或 Windows 上安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，并使用能运行本机命令、访问当前系统用户凭据库的 Agent 会话。如果仓库是私有的，请先在本机配置有读取权限的 GitHub 凭据。

### 用 Skills CLI 安装

先安装 Node.js 22.20 或更新版本。 [Skills CLI 安装要求](https://github.com/vercel-labs/skills#install-a-skill)

```sh
npx skills add SII-OI/sii-long-profile-skill -g
```

CLI 会自动选中仓库里的 Skill，并检测本机 Agent。出现选择提示时，选你平时使用的 Agent。`-g` 将 Skill 安装到用户目录，换项目也能用。只在一个项目里用时，在该项目目录运行并省略 `-g`。

需要指定 Agent 时，才在安装命令末尾加上表中的 `-a` 参数。

| Agent | `-a` 参数 | 用户级 Skill 目录 |
| --- | --- | --- |
| Codex | `codex` | `~/.agents/skills/` |
| Claude Code | `claude-code` | `~/.claude/skills/` |
| Cursor | `cursor` | `~/.cursor/skills/` |
| Gemini CLI | `gemini-cli` | `~/.gemini/skills/` |
| GitHub Copilot | `github-copilot` | `~/.copilot/skills/` |
| OpenCode | `opencode` | `~/.config/opencode/skills/` |
| Windsurf | `windsurf` | `~/.codeium/windsurf/skills/` |
| Kimi Code CLI | `kimi-code-cli` | `~/.agents/skills/` |
| ZCode | `zcode` | `~/.zcode/skills/` |

安装参数和目录可在官方文档核对。 [Skills CLI 的 Agent 列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) · [Kimi Code CLI](https://www.kimi.com/code/docs/kimi-code-cli/customization/skills.html) · [ZCode](https://zcode.z.ai/cn/docs/skill)

安装后，可以运行 `npx skills ls -g` 查看用户级 Skill，或在所选 Agent 的 Skill 列表里搜索 `sii-long-profile`。项目级安装用 `npx skills ls`。确认已安装后，按第 2 节配置令牌。如果 Agent 的列表还未刷新，请重开会话。 [查看已安装的 Skill](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#skills-list)

### DeepSeek Harness 和 WorkBuddy

先安装 Git 并下载 Skill。如果 DeepSeek Harness 已经可以从 `~/.agents/skills/sii-long-profile/` 发现此 Skill，可以直接配置令牌。

```sh
git clone https://github.com/SII-OI/sii-long-profile-skill.git sii-long-profile-source
cd sii-long-profile-source
```

#### DeepSeek Harness

1. 在用户目录下创建 `~/.dsh/skills/sii-long-profile/`。如果设置了 `DSH_HOME`，则在该目录下创建 `skills/sii-long-profile/`。
2. 从下载目录复制 `SKILL.md`、`scripts/` 和 `references/` 到上一步创建的目录，确保 `SKILL.md` 位于 `sii-long-profile/` 的第一层。
3. 打开本地 Harness 会话，确认技能列表中出现 `sii-long-profile`，再进入复制后的目录配置令牌。 [DeepSeek Harness 技能发现规则](https://deepseek-harness.github.io/deepseek-harness/en/reference/subsystems/skills) · [默认目录说明](https://github.com/deepseek-ai/deepseek-harness/blob/master/packages/skill/skill-filesystem/README.md)

#### WorkBuddy

1. 在下载目录运行下面的命令，生成 `sii-long-profile.zip`。

   ```sh
   git archive --format=zip --prefix=sii-long-profile/ --output=sii-long-profile.zip HEAD SKILL.md scripts references
   ```

2. 在 WorkBuddy 打开「技能 → 添加技能 → 上传技能」，选择刚生成的 ZIP。确认已安装的技能列表中出现 `sii-long-profile`。 [WorkBuddy 技能导入说明](https://intl.cloud.tencent.com/zh/document/product/1316/84503)
3. 在本机终端留在下载目录，按第 2 节配置令牌。之后在 WorkBuddy 的本地工作台调用 Skill。

已在 macOS 上验证脚本的令牌配置和连接检查。各 Agent 内的安装和端到端调用待实测。

## 2. 配置创智龙令牌

1. 用飞书登录 [创智龙](https://oi.scion.org.cn/cz-long/)，进入「设置 → API 令牌」，生成并复制自己的令牌。账号需已核验并关联本人教师档案。
2. 在本机终端进入包含 `SKILL.md` 和 `scripts/` 的 Skill 目录，再运行配置命令。WorkBuddy 用户可以直接在下载目录运行 `uv run --script scripts/research_profile.py configure`。下面以 Codex 的目录为例。

   ```sh
   cd ~/.agents/skills/sii-long-profile
   uv run --script scripts/research_profile.py configure
   ```

3. 按终端提示粘贴令牌。输入不会回显。脚本会把令牌保存到 macOS 钥匙串或 Windows 凭据管理器。终端显示本人的姓名和档案 ID，说明连接成功。

随时可以在同一目录运行 `uv run --script scripts/research_profile.py check` 检查连接。令牌过期或撤销后，在创智龙生成新令牌并重新运行 `configure`。

## 3. 在 Agent 中使用

打开 Agent 的本地会话，选择或点名使用 `sii-long-profile`。Kimi Code CLI 可输入 `/skill:sii-long-profile`，ZCode 可在「设置 → 技能」确认已启用。先试第一条指令，返回本人姓名后再尝试查询和修改成果。

- 检查连接，告诉我当前关联的导师姓名。
- 列出我的论文和项目，并标明审核状态。
- 找到我指定的论文，预览发表渠道的修改，等我确认后再保存草稿。

保存成功后，可在创智龙「我的科研资料」看到草稿。送审前，Skill 会列出本次要提交的全部待提交草稿，其中也包括网页上已保存的草稿。

也可以在本机终端进入 Skill 目录，运行 `uv run --script scripts/research_profile.py list`，直接查看本人的论文和项目。脚本在本机运行，读取和修改科研资料时会调用创智龙 API，需要联网。

更多命令和字段见 [Skill 说明](SKILL.md) 与 [成果字段](references/fields.md)。
