# Claude Skills & Commands Sync

跨设备同步 Claude Code 的 skills 和 commands 的仓库。

## 目录结构

```
claude-skills/
├── commands/          # Claude commands (.md files)
├── skills/            # Claude skills (.md files)
├── sync.py            # 同步脚本
└── README.md          # 本文件
```

## 使用方法

### 1. 克隆仓库

```bash
git clone https://github.com/santashen/claude-skills.git
cd claude-skills
```

### 2. 运行同步脚本

**Windows:**
```cmd
python sync.py
```

**macOS/Linux:**
```bash
python3 sync.py
```

### 3. 配置选项

```bash
# 强制复制而不是创建符号链接
python sync.py --copy

# 预览模式（不实际修改文件）
python sync.py --dry-run

# 指定自定义的 Claude 配置路径
python sync.py --config-path /path/to/claude/config
```

## 支持的平台

| 操作系统 | Claude 配置路径 |
|---------|---------------|
| Windows | `%APPDATA%\Claude\` |
| macOS | `~/Library/Application Support/Claude/` |
| Linux | `~/.config/Claude/` |

## 添加新的 Skill 或 Command

1. 将 `.md` 文件放入对应的目录：
   - Skills 放入 `skills/` 目录
   - Commands 放入 `commands/` 目录

2. 运行同步脚本：
   ```bash
   python sync.py
   ```

3. 重启 Claude Code 使更改生效

## 同步到其他设备

1. 提交更改到 Git：
   ```bash
   git add .
   git commit -m "Add new skill/command"
   git push
   ```

2. 在其他设备上拉取更新：
   ```bash
   git pull
   python sync.py
   ```
