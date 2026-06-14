# 🐍 Python 虚拟环境配置记录

> **配置日期：** 2026-06-13  
> **目标读者：** 下一个接手此项目的 AI Agent / 开发者

---

## 一、最终环境状态

| 项目 | 详情 |
|------|------|
| **虚拟环境目录** | `venv\`（项目根目录） |
| **Python 路径** | `venv\Scripts\python.exe` |
| **pip 路径** | `venv\Scripts\pip.exe` |
| **Python 版本** | 3.14.3 |
| **pip 版本** | 25.3 |
| **已安装包** | openpyxl, pdfplumber, jupyter 及其依赖 |
| **系统 Python** | `C:\Users\s1325\AppData\Local\Programs\Python\Python314\python.exe` |
| **VS Code Pylance** | 已指向 `venv\Scripts\python.exe` |

---

## 二、激活方式

### PowerShell（推荐）

```powershell
.\venv\Scripts\Activate.ps1
```

### 直接调用（无需激活）

```powershell
& "venv\Scripts\python.exe" script.py
& "venv\Scripts\pip.exe" install <package>
```

---

## 三、配置过程中遇到的问题

### 问题 1：旧记录（历史问题，本次未遇到）

- 历史上有 `.venv` 创建失败的问题，本次重建使用 `venv\` 目录顺利完成。
  - ❌ 换到 `C:\temp` 创建 — 无写入权限
- **最终解决：** 改用新目录名 `venv`（而非 `.venv`），一次创建成功

### 问题 2：残留 `.venv` 目录无法删除

- **现象：** `Remove-Item -Recurse -Force .venv` 返回"拒绝访问"
- **解决：** 后续通过 `cmd /c rmdir /s /q` 成功清理

### 问题 3：PowerShell 路径中包含 `--` 导致解析错误

- **现象：** 在 PowerShell 中用引号路径直接拼接 `;` 会触发行尾解析错误
- **正确写法：** 使用 `&` 调用运算符，例如 `& "path\to\python.exe" --version`

---

## 四、已知注意事项

1. **不要使用 `.venv` 作为虚拟环境目录名** — 该名称曾被锁定，虽已清理，但为避免潜在问题，统一使用 `venv\`
2. **项目无 `.gitignore`** — 建议创建并将 `venv/` 加入忽略列表
3. **Python 3.14.3 较新** — 部分第三方包可能尚未完全兼容，安装前需留意
4. **系统未安装 Conda** — 只有系统级 Python 3.14，所有依赖通过 pip 管理
5. **路径含中文字符** — 项目路径 `生物多样性比赛\Biodiversity_competition\` 含中文，部分工具可能受影响，目前 venv 工作正常

---

## 五、快速恢复指南

如果虚拟环境损坏需要重建：

```powershell
# 1. 删除旧环境
cmd /c "rmdir /s /q venv"

# 2. 重建
C:\Users\s1325\AppData\Local\Programs\Python\Python314\python.exe -m venv venv

# 3. 升级 pip（可选）
& "venv\Scripts\python.exe" -m pip install --upgrade pip

# 4. 安装项目依赖（如有 requirements.txt）
& "venv\Scripts\pip.exe" install -r requirements.txt
```

---

*本文档由 GitHub Copilot 在配置 Python 环境时自动生成*
