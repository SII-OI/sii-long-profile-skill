# 创智龙科研资料助手

`sii-long-profile` 是一个 Codex Skill，用于查询和维护导师本人的论文与项目。它可以预览改动、保存草稿，并在导师确认后提交审核。

## 1. 安装

使用 macOS 或 Windows 上的 Codex 本地会话。先在本机安装 Node.js 22.20 或更新版本，以及 [uv](https://docs.astral.sh/uv/getting-started/installation/)。如果仓库是私有的，请先确认本机已配置有读取权限的 GitHub 凭据。 [Skills CLI 安装要求](https://github.com/vercel-labs/skills#install-a-skill)

在本机终端运行：

```sh
npx skills add SII-OI/sii-long-profile-skill --skill sii-long-profile -a codex -g
```

安装后，在 Codex 的 Skill 列表中应能看到 `sii-long-profile`。如果列表还未刷新，请重启 Codex。

## 2. 配置创智龙令牌

1. 用飞书登录 [创智龙](https://oi.scion.org.cn/cz-long/)，进入「设置 → API 令牌」，生成并复制自己的令牌。账号需已核验并关联本人教师档案。
2. 在本机终端进入 Skill 目录，运行配置命令：

   ```sh
   cd ~/.agents/skills/sii-long-profile
   uv run --script scripts/research_profile.py configure
   ```

3. 按终端提示粘贴令牌。输入不会回显。脚本会把令牌保存到 macOS 钥匙串或 Windows 凭据管理器。终端显示本人的姓名和档案 ID，说明连接成功。

随时可以在同一目录运行 `uv run --script scripts/research_profile.py check` 检查连接。令牌过期或撤销后，在创智龙生成新令牌并重新运行 `configure`。

## 3. 在 Codex 中使用

打开 Codex 本地会话，选择 `sii-long-profile`，试试以下指令：

- 检查连接，告诉我当前关联的导师姓名。
- 列出我的论文和项目，并标明审核状态。
- 找到我指定的论文，预览发表渠道的修改，等我确认后再保存草稿。

保存成功后，可在创智龙「我的科研资料」看到草稿。送审前，Skill 会列出本次要提交的全部待提交草稿，其中也包括网页上已保存的草稿。

更多命令和字段见 [Skill 说明](SKILL.md) 与 [成果字段](references/fields.md)。
