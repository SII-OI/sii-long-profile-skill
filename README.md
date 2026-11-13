# 创智龙科研资料助手

`sii-long-profile` 是一个本地 Agent Skill，用于查询和维护导师本人的论文与项目。Agent 会收集资料并整理成预览，导师确认后直接提交审核。

## 1. 安装

在 macOS 或 Windows 上使用能运行本机脚本的 Agent 会话。配置令牌时推荐使用 `uv`，安装方法见第 2 节。如果仓库是私有的，请先在本机配置有读取权限的 GitHub 凭据。

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

### 查看本机版本

进入已安装的 Skill 目录后运行以下命令。输出包含 Skill 名称和版本号，配置令牌前也可以查看。

```sh
uv run --script scripts/research_profile.py --version
```

## 2. 配置创智龙令牌

Skill 默认连接开发机。请在开发机生成令牌，账号需已核验并关联本人教师档案。 [打开创智小龙开发机](https://118.196.149.115:8430/)

脚本会自动使用随 Skill 安装的开发机证书。升级 Skill 后，已配置令牌的用户可以直接运行 `check`。开发机换证后，维护者需要用运维提供的新公开证书替换 `scripts/certs/cz-long-118-8430.pem`，用户更新 Skill 后即可继续使用。

如果用 `--base-url` 连接其他实例，而该实例使用自签名证书，请向运维获取可信 PEM 证书，再将运行脚本的进程的 `SSL_CERT_FILE` 设置为证书的绝对路径。

在本机终端进入包含 `SKILL.md` 和 `scripts/` 的 Skill 目录。以 Codex 的用户级安装为例，运行 `cd ~/.agents/skills/sii-long-profile`。WorkBuddy 用户可在生成 ZIP 时使用的下载目录运行下面的命令。

### 使用 uv（推荐）

1. 如果还没装 `uv`，在 macOS 上可以用 Homebrew 运行 `brew install uv`，在 Windows 上可以运行 `winget install --id=astral-sh.uv -e`。如果没有对应的包管理器，按官方文档使用独立安装方式。装完重新打开终端，运行 `uv --version`，看到版本号后回到 Skill 目录。 [uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)
2. 在 Skill 目录运行配置命令。

   ```sh
   uv run --script scripts/research_profile.py configure
   ```

3. 用飞书登录创智小龙开发机，进入「设置 → API 令牌」，生成并复制自己的 API Key。看到本机终端提示「粘贴创智龙 API 令牌（输入不显示）」后，粘贴令牌并按回车。验证通过后，脚本会将令牌保存到 macOS 钥匙串或 Windows 凭据管理器。
4. 在同一目录运行 `check`，确认授权成功。

   ```sh
   uv run --script scripts/research_profile.py check
   ```

   返回的 `profile.name` 和 `profile.id` 应对应本人的教师档案。成功返回示例如下，档案 ID 和成果数量以实际返回为准。

   ```json
   {
     "profile": {
       "id": "manual:0123456789abcdef01234567",
       "name": "示例导师"
     },
     "binding_revision": 1,
     "archived_count": 0,
     "record_count": 2
   }
   ```

### 使用 Python 配置（无需 uv）

如果本机已有 Python 3.11 或更新版本，可以在 Skill 目录执行对应系统的命令。虚拟环境建在用户目录，供后续运行脚本使用。

**macOS**

```sh
python3 -m venv "$HOME/.sii-long-profile-venv"
"$HOME/.sii-long-profile-venv/bin/python" -m pip install "keyring>=25,<26"
"$HOME/.sii-long-profile-venv/bin/python" scripts/research_profile.py configure
```

**Windows PowerShell**

```powershell
py -3 -m venv "$HOME/.sii-long-profile-venv"
& "$HOME/.sii-long-profile-venv/Scripts/python.exe" -m pip install "keyring>=25,<26"
& "$HOME/.sii-long-profile-venv/Scripts/python.exe" scripts/research_profile.py configure
```

按上面的第 3 步生成并粘贴令牌，再把对应 Python 命令末尾的 `configure` 换成 `check`，按第 4 步核对返回的档案。继续使用这套环境时，在 Agent 对话里明确指定用该虚拟环境的 Python 运行 Skill 脚本。当前 `SKILL.md` 的默认运行方式是 `uv run --script`。

令牌过期或撤销后，在创智小龙生成新令牌，再运行 `configure`。

## 3. 在 Agent 中使用

打开 Agent 的本地会话，选择或点名使用 `sii-long-profile`。Kimi Code CLI 可输入 `/skill:sii-long-profile`，ZCode 可在「设置 → 技能」确认已启用。先试第一条指令，返回本人姓名后再尝试查询和修改成果。

- 检查连接，告诉我当前关联的导师姓名。
- 列出我的论文和项目，并标明审核状态。
- 找到我指定的论文，预览发表渠道的修改，等我确认后直接送审。
- 我想新增一个项目，请告诉我需要提供哪些信息。

请核对 Agent 发来的预览，再明确回复「确认提交」。送审只包含本次预览的条目。Agent 返回「已提交审核」后，可在创智龙「我的科研资料 → 论文与项目」查看审核状态。

也可以在本机终端进入 Skill 目录，运行 `uv run --script scripts/research_profile.py list`，直接查看本人的论文和项目。脚本在本机运行，读取和修改科研资料时会调用创智龙 API，需要联网。

更多命令和字段见 [Skill 说明](SKILL.md) 与 [成果字段](references/fields.md)。
