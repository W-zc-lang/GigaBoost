# ⚡ GigaBoost · 千兆宽带 WiFi 5G 加速神器

> 办了千兆宽带却跑不满？多半是网卡被默认连到拥挤的 **2.4GHz**。GigaBoost 一键强制优先 **5GHz** 并关闭电源节能，全程无需打开设备管理器，兼容 Windows 10 / 11。

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)](https://www.microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/W-zc-lang/GigaBoost?label=Release)](https://github.com/W-zc-lang/GigaBoost/releases)

## ✨ 亮点

- **一键 5GHz**：强制网卡优先连接 5GHz 频段
- **关闭节能**：避免系统为了省电降速
- **零配置**：图形界面，无需设备管理器
- **兼容广**：Windows 10 / 11 各版本

## 🚀 下载

👉 **[GitHub Releases 下载 GigaBoost](https://github.com/W-zc-lang/GigaBoost/releases)**

## ☕ 支持

点个 **Star** ⭐ 支持作者。

---


## ✨ 亮点

- **一键 5GHz**：强制网卡优先连接 5GHz 频段
- **关闭节能**：避免系统为了省电降速
- **零配置**：图形界面，无需设备管理器
- **兼容广**：Windows 10 / 11 各版本

## 🚀 下载

👉 **[GitHub Releases 下载 GigaBoost](https://github.com/W-zc-lang/GigaBoost/releases)**

## ☕ 支持

点个 **Star** ⭐ 支持作者。

---


## ✨ 功能亮点

- 🚀 **一键增强**：点一下按钮，自动完成全部优化，无需任何手动设置。
- 🛡️ **自动提权**：首次运行自动请求管理员权限，改得了网卡高级属性。
- 📡 **强制 5GHz 优先**：把网卡「首选频带」设为「首选 5 GHz 频带」，避开 2.4G 干扰与限速。
- 💤 **关闭电源节能**：注册表 `PnPCapabilities=24`，禁止系统为省电关闭网卡，降低延迟抖动。
- 📊 **优化前后对比**：实测优化前后连接速率与下载速率，给出提升数据。
- 🪟 **大界面图形交互**：窗口放大至 1080×980 且可自由缩放，介绍页 + 增强过程 5 步详解 + 实时日志，纯小白也能看懂。
- 🎯 **醒目增强按钮**：独立浅绿高亮卡片 + 大号按钮「🚀 开始增强网速」，再也不会“找不到按钮”。
- 🎨 **白色清爽主题 + 高分屏适配**：高 DPI 字体自动缩放、界面清晰不模糊，配全新绿色品牌图标。
- 🔧 **免设备管理器**：所有操作后台完成，不用你去找网卡属性。

---

## 🔍 为什么需要它

千兆宽带入户后，瓶颈常常不在运营商，而在你家里的无线连接：

1. **2.4GHz 频段** 理论速率低、信道拥挤（邻居 WiFi、蓝牙、微波炉都来抢），很容易把千兆“掐”到一两百兆。
2. 系统默认**不强制 5GHz**，信号弱一点就自动跳回 2.4G。
3. 网卡「允许计算机关闭此设备以节约电源」会在空闲时休眠，造成延迟抖动、掉速。

GigaBoost 做的，就是**把 5GHz 设为硬性优先 + 关掉节能**，让高速频段稳稳在线。

---

## 🧩 增强原理（5 步详解）

| 步骤 | 操作 | 作用 |
|------|------|------|
| ① | **自动提权** | 请求管理员权限，以修改网卡高级属性与注册表 |
| ② | **自动识别网卡** | 按硬件类型 / 驱动名 / 接口名智能匹配，兼容 `Wi-Fi`、`WLAN`、无线网络等命名 |
| ③ | **首选 5GHz 频带** | 将网卡「首选频带」设为「首选 5 GHz 频带」，强制优先连接 5G WiFi |
| ④ | **关闭电源节能** | 修改注册表 `PnPCapabilities=24`，禁止系统为省电关闭网卡 |
| ⑤ | **重启生效 + 对比** | 重启无线适配器，并实测优化前后速率，给出提升数据 |

> 说明：脚本会真正改动系统网卡高级属性与注册表。若 5GHz 信号本身弱于 2.4GHz，
> 系统仍可能择优连接——这是硬件覆盖行为，非脚本问题。请尽量靠近路由器使用 5G WiFi。

---

## 📥 使用步骤

1. 到 [Releases](https://github.com/W-zc-lang/GigaBoost/releases) 下载 `GigaBoost.exe`。
2. **右键 → 以管理员身份运行**（或直接双击，程序会请求 UAC 提权）。
3. 阅读介绍与「增强原理」后，点击 **「开始增强网速」** 按钮。
4. 等待实时日志跑完，弹出「优化完成」结果框，查看速率提升。
5. 如需恢复，可在设备管理器把「首选频带」改回「自动 / 无偏好」，并删除对应网卡注册表项
   `HKLM\SYSTEM\CurrentControlSet\Enum\<设备ID>\Device Parameters` 下的 `PnPCapabilities`。

---

## 🛠️ 从源码运行 / 自行打包

```bash
# 依赖：Python 3.10+（需自带 tkinter）
pip install pyinstaller

# 直接运行图形界面
python app.py

# 打包为单文件管理员 EXE
pyinstaller --onefile --windowed --uac-admin --icon=icon.ico --name GigaBoost app.py
# 产物位于 dist/GigaBoost.exe
```

源码 `app.py` 中内嵌了优化用的 PowerShell 脚本，运行时通过系统 `powershell.exe` 执行，
因此本工具**不依赖任何第三方运行时**，纯 Windows 原生环境即可工作。

---

## ⚠️ 注意事项

- 仅适用于 **Windows 10 / 11** 的无线（Wi‑Fi）网卡。
- 需要**管理员权限**才能修改网卡属性与注册表。
- 部分笔记本的无线网卡驱动可能不存在「首选频带」选项，此时脚本会跳过该项并提示，不影响其余优化。
- 5GHz WiFi 覆盖范围小于 2.4GHz，请确保设备在 5G 信号覆盖内。

---

## 📜 免责声明

本工具按「现状」提供，仅供个人学习与优化使用。修改系统网络设置存在一定风险，
请在理解原理后使用；因使用本工具导致的任何网络异常或系统问题，作者不承担责任。

---

## 📄 开源许可

[MIT License](LICENSE) © W-zc-lang
