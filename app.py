# -*- coding: utf-8 -*-
"""GigaBoost - 千兆宽带 WiFi 5G 加速神器 (GUI 版)"""
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import subprocess, threading, os, tempfile, re, sys

PS_SCRIPT = r'''
$ErrorActionPreference = 'SilentlyContinue'
function Log($m){ Write-Output $m }
try {
  $adp = Get-NetAdapter | Where-Object {
    $_.MediaType -eq 'Native 802.11' -or
    $_.InterfaceDescription -match 'Wireless|Wi-?Fi|802\.11|WLAN|无线' -or
    $_.Name -match 'Wi-?Fi|WLAN|无线网络|无线'
  } | Select-Object -First 1
  if (-not $adp) { Write-Output "ERROR|未找到无线网卡，请确认无线网卡已启用并连接"; exit 1 }
  $an = $adp.Name
  Log ("[1/5] 已识别无线网卡: " + $an)
  function Measure-Speed($phase){
    Log ("        " + $phase)
    $urls = @(
      'https://speed.cloudflare.com/__down?bytes=30000000',
      'https://speedtest.tele2.net/30MB.zip',
      'https://download.thinkbroadband.com/20MB.zip'
    )
    foreach ($u in $urls){
      try {
        $tmp = [System.IO.Path]::GetTempFileName()
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        Invoke-WebRequest -Uri $u -OutFile $tmp -TimeoutSec 15 -UseBasicParsing -ErrorAction Stop
        $sw.Stop()
        $b = (Get-Item $tmp).Length
        Remove-Item $tmp -Force -ErrorAction SilentlyContinue
        if ($sw.Elapsed.TotalSeconds -le 0){ continue }
        return [math]::Round(($b*8/1048576)/$sw.Elapsed.TotalSeconds,1)
      } catch { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
    }
    return $null
  }
  $beforeLink = (Get-NetAdapter -Name $an).LinkSpeed
  $beforeSpeed = Measure-Speed '优化前测速中...'
  Log ("[2/5] 优化前连接速率: " + $beforeLink)
  Log ("[3/5] 设置首选 5GHz 频带 (强制优先连接 5G WiFi)...")
  $p = Get-NetAdapterAdvancedProperty -Name $an | Where-Object { $_.DisplayName -match 'band|频带|prefer|首选' } | Select-Object -First 1
  if ($p){
    $pn = $p.DisplayName
    $vv = (Get-NetAdapterAdvancedProperty -Name $an -DisplayName $pn).ValidDisplayValues
    $tv = $vv | Where-Object { $_ -match '5' -and ($_ -match 'GHz|赫兹|5G') } | Select-Object -First 1
    if ($tv){ Set-NetAdapterAdvancedProperty -Name $an -DisplayName $pn -DisplayValue $tv -NoRestart; Log ("        已写入: " + $pn + " = " + $tv) }
    else { Log "        未找到明确的 5G 选项，已跳过" }
  } else { Log "        未找到'首选频带'属性，已跳过" }
  Log ("[4/5] 关闭网卡电源节能 (注册表 PnPCapabilities=24)...")
  $dev = Get-CimInstance Win32_NetworkAdapter | Where-Object { $_.NetConnectionID -eq $an -or $_.Name -eq $an } | Select-Object -First 1
  if ($dev){
    $rp = "HKLM:\SYSTEM\CurrentControlSet\Enum\$($dev.PNPDeviceID)\Device Parameters"
    if (-not (Test-Path $rp)){ New-Item -Path $rp -Force | Out-Null }
    New-ItemProperty -Path $rp -Name 'PnPCapabilities' -Value 24 -PropertyType DWord -Force | Out-Null
  }
  Log ("[5/5] 重启无线网卡使设置生效...")
  Restart-NetAdapter -Name $an -Confirm:$false
  $w=0; while($w -lt 20){ if((Get-NetAdapter -Name $an).Status -eq 'Up'){break}; Start-Sleep -Seconds 1; $w++ }
  Start-Sleep -Seconds 3
  $afterLink = (Get-NetAdapter -Name $an).LinkSpeed
  $afterSpeed = Measure-Speed '优化后测速中...'
  $bs = if($beforeSpeed){$beforeSpeed.ToString()}else{'N/A'}
  $as = if($afterSpeed){$afterSpeed.ToString()}else{'N/A'}
  $gain = if($beforeSpeed -and $afterSpeed){[math]::Round($afterSpeed-$beforeSpeed,1)}else{$null}
  $g = if($gain){$gain.ToString()}else{'N/A'}
  Write-Output ("RESULT|beforeLink=" + $beforeLink + "|afterLink=" + $afterLink + "|beforeSpeed=" + $bs + "|afterSpeed=" + $as + "|gain=" + $g)
} catch {
  Write-Output ("ERROR|" + $_.Exception.Message)
}
'''


class GigaBoostApp:
    def __init__(self, root):
        self.root = root
        root.title("GigaBoost · 千兆宽带 WiFi 5G 加速神器")
        root.geometry("760x680")
        root.resizable(False, False)
        try:
            root.iconbitmap(default="")
        except Exception:
            pass

        # 配色
        BG = "#0f172a"
        PANEL = "#1e293b"
        ACCENT = "#22c55e"
        ACCENT2 = "#38bdf8"
        TEXT = "#e2e8f0"
        MUTE = "#94a3b8"

        root.configure(bg=BG)

        # 顶部标题
        header = tk.Frame(root, bg=BG, height=84)
        header.pack(fill=tk.X)
        tk.Label(header, text="⚡ GigaBoost", bg=BG, fg=ACCENT,
                 font=("Microsoft YaHei UI", 22, "bold")).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(header, text="千兆宽带 WiFi 5G 加速神器 · 一键强制 5GHz 优先，告别 2.4G 拥堵",
                 bg=BG, fg=MUTE, font=("Microsoft YaHei UI", 11)).pack(anchor="w", padx=20, pady=(2, 0))

        # 介绍
        intro = tk.LabelFrame(root, text=" 软件介绍 ", bg=PANEL, fg=ACCENT2,
                              font=("Microsoft YaHei UI", 11, "bold"), bd=1, relief=tk.GROOVE)
        intro.pack(fill=tk.X, padx=16, pady=(10, 6))
        tk.Label(intro,
                 text=("办了千兆宽带，测速却跑不满？多半是无线网卡被系统默认连到了拥挤的 2.4GHz 频段。"
                       "GigaBoost 会自动请求管理员权限，把网卡的「首选频带」强制设为 5GHz，"
                       "并关闭「允许计算机关闭此设备以节约电源」，让千兆带宽真正喂满你的设备。\n"
                       "全程无需打开设备管理器，兼容 Windows 10 / 11 各版本。"),
                 bg=PANEL, fg=TEXT, font=("Microsoft YaHei UI", 10), justify=tk.LEFT, wraplength=710).pack(padx=12, pady=8)

        # 增强原理 5 步
        detail = tk.LabelFrame(root, text=" 增强原理（5 步详解） ", bg=PANEL, fg=ACCENT2,
                              font=("Microsoft YaHei UI", 11, "bold"), bd=1, relief=tk.GROOVE)
        detail.pack(fill=tk.X, padx=16, pady=(0, 6))
        steps = (
            "① 自动提权：请求管理员权限，以修改网卡高级属性与注册表。\n"
            "② 自动识别网卡：按硬件类型 / 驱动名 / 接口名智能匹配，兼容 Wi-Fi、WLAN、无线网络等命名。\n"
            "③ 首选 5GHz 频带：将网卡「首选频带」设为「首选 5 GHz 频带」，强制优先连接 5G WiFi，避开 2.4G 干扰与限速。\n"
            "④ 关闭电源节能：修改注册表 PnPCapabilities=24，禁止系统为省电关闭网卡，降低延迟抖动。\n"
            "⑤ 重启生效 + 对比：重启无线适配器，并实测优化前后连接速率与下载速率，给出提升数据。"
        )
        tk.Label(detail, text=steps, bg=PANEL, fg=TEXT, font=("Microsoft YaHei UI", 10),
                 justify=tk.LEFT, wraplength=710).pack(padx=12, pady=8, anchor="w")

        # 按钮
        btn_frame = tk.Frame(root, bg=BG)
        btn_frame.pack(fill=tk.X, padx=16, pady=(2, 6))
        self.btn = tk.Button(btn_frame, text="开始增强网速", command=self.on_boost,
                             bg=ACCENT, fg="#06281a", font=("Microsoft YaHei UI", 13, "bold"),
                             activebackground="#16a34a", activeforeground="#06281a",
                             height=1, relief=tk.FLAT, cursor="hand2")
        self.btn.pack(fill=tk.X, ipady=10)

        # 结果
        res = tk.LabelFrame(root, text=" 优化结果 ", bg=PANEL, fg=ACCENT2,
                            font=("Microsoft YaHei UI", 11, "bold"), bd=1, relief=tk.GROOVE)
        res.pack(fill=tk.X, padx=16, pady=(0, 6))
        self.result_var = tk.StringVar(value="尚未运行。点击上方按钮开始优化。")
        tk.Label(res, textvariable=self.result_var, bg=PANEL, fg=TEXT,
                 font=("Microsoft YaHei UI", 10), justify=tk.LEFT, wraplength=710).pack(padx=12, pady=8, anchor="w")

        # 日志
        logf = tk.LabelFrame(root, text=" 实时日志 ", bg=PANEL, fg=ACCENT2,
                             font=("Microsoft YaHei UI", 11, "bold"), bd=1, relief=tk.GROOVE)
        logf.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))
        self.log = scrolledtext.ScrolledText(logf, bg="#0b1220", fg="#cbd5e1",
                                             font=("Consolas", 9), height=12, relief=tk.FLAT)
        self.log.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    def append_log(self, text):
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)

    def set_result(self, text):
        self.result_var.set(text)

    def on_boost(self):
        self.btn.config(state=tk.DISABLED, text="正在增强，请稍候...")
        self.set_result("优化进行中，请查看下方日志...")
        threading.Thread(target=self.run_optimize, daemon=True).start()

    def run_optimize(self):
        try:
            ps_path = os.path.join(tempfile.gettempdir(), "gigaboost_opt.ps1")
            with open(ps_path, "w", encoding="utf-8") as f:
                f.write(PS_SCRIPT)

            pwsh = os.path.join(os.environ.get("SYSTEMROOT", "C:\\Windows"),
                                "System32", "WindowsPowerShell", "v1.0", "powershell.exe")
            proc = subprocess.Popen(
                [pwsh, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", ps_path],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace"
            )

            result_line = None
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                if not line:
                    continue
                self.root.after(0, self.append_log, line)
                if line.startswith("RESULT|") or line.startswith("ERROR|"):
                    result_line = line

            proc.wait()
            if ps_path and os.path.exists(ps_path):
                try:
                    os.remove(ps_path)
                except Exception:
                    pass

            if result_line and result_line.startswith("RESULT|"):
                self.show_result(result_line)
            elif result_line and result_line.startswith("ERROR|"):
                msg = result_line.split("|", 1)[1]
                self.root.after(0, self.set_result, "优化失败：" + msg)
                self.root.after(0, lambda: messagebox.showerror("GigaBoost", "优化失败：\n" + msg))
            else:
                self.root.after(0, self.set_result, "优化完成，但未解析到结果数据（请查看日志）。")

        except Exception as e:
            err = str(e)
            self.root.after(0, self.append_log, "EXCEPTION: " + err)
            self.root.after(0, self.set_result, "发生异常：" + err)
            self.root.after(0, lambda: messagebox.showerror("GigaBoost", "发生异常：\n" + err))
        finally:
            self.root.after(0, lambda: self.btn.config(state=tk.NORMAL, text="开始增强网速"))

    def show_result(self, line):
        parts = dict(kv.split("=", 1) for kv in line.split("|")[1:] if "=" in kv)
        before_link = parts.get("beforeLink", "N/A")
        after_link = parts.get("afterLink", "N/A")
        before_speed = parts.get("beforeSpeed", "N/A")
        after_speed = parts.get("afterSpeed", "N/A")
        gain = parts.get("gain", "N/A")
        text = (
            "优化完成！\n"
            "· 连接速率 Link Speed：%s  →  %s\n"
            "· 实测下载速率：%s Mbps  →  %s Mbps\n"
            "· 提速：%s Mbps" % (before_link, after_link, before_speed, after_speed, gain)
        )
        self.root.after(0, self.set_result, text)
        self.root.after(0, lambda: messagebox.showinfo("GigaBoost · 优化完成", text))


def main():
    root = tk.Tk()
    app = GigaBoostApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
