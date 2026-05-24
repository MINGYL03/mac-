# 批量照片加 Logo / 水印工具

这是一个带图形界面的批量照片加 Logo / 水印工具。用户可以选择照片文件夹、Logo 图片和输出文件夹，在界面中调整 Logo 的大小、透明度和位置，并支持直接在预览图上拖动 Logo，最后批量导出处理后的图片。

本项目支持两种使用方式：

1. **在线编译**：不需要在自己电脑上配置打包环境，直接使用 GitHub Actions 在线生成 Windows 或 macOS 可执行程序。
2. **下载源码本地运行/编译**：把项目下载到自己的电脑上，通过 Python 运行源码，也可以本地打包成 exe 或 app。

---

## 功能特点

* 支持批量给照片添加 Logo / 水印
* 支持图形化界面操作
* 支持选择照片文件夹、Logo 图片和输出文件夹
* 支持调整 Logo 大小、透明度、水平位置和垂直位置
* 支持在预览图中直接拖动 Logo
* 支持常见图片格式：`.jpg`、`.jpeg`、`.png`、`.webp`、`.bmp`、`.tif`、`.tiff`
* 支持保持原格式输出，也可以统一输出为 JPG 或 PNG
* 支持设置 JPG 输出质量
* 支持输出文件名自动添加 `_logo` 后缀，避免覆盖原图

---

## 项目文件说明

```text
.
├── logo_batch_gui.py                    # 主程序
├── requirements.txt                     # Python 依赖
└── .github/workflows/
    ├── mac-build.yml 或 main.yml         # macOS 在线编译配置
    └── build-windows.yml                # Windows 在线编译配置
```

如果你的仓库中 workflow 文件名不同，只要它们位于 `.github/workflows/` 文件夹中即可正常被 GitHub Actions 识别。

---

# 使用方式一：在线编译生成可执行程序

在线编译适合不想在本地配置 PyInstaller 的用户。GitHub 会自动使用 Windows 或 macOS 云端环境打包程序，打包完成后可以直接下载成品。

## 1. 在线编译 Windows 版 exe

1. 打开本项目 GitHub 仓库页面。
2. 点击顶部的 **Actions**。
3. 在左侧选择 **build Windows exe**。
4. 点击右侧的 **Run workflow**。
5. 等待运行完成，看到绿色对勾表示编译成功。
6. 打开本次运行记录。
7. 在页面下方的 **Artifacts** 区域下载：

```text
LogoBatchTool-Windows
```

8. 下载后解压，得到：

```text
批量加Logo工具.exe
```

9. 双击 `批量加Logo工具.exe` 即可运行。

### Windows 安全提示

由于程序是通过 PyInstaller 打包生成的，部分杀毒软件或 Windows 安全中心可能会出现安全提醒。如果你确认代码来自本仓库，可以选择允许运行。若担心误报，也可以下载源码后在本地自行运行或编译。

---

## 2. 在线编译 macOS 版 app

1. 打开本项目 GitHub 仓库页面。
2. 点击顶部的 **Actions**。
3. 在左侧选择 **build macOS app**。
4. 点击右侧的 **Run workflow**。
5. 等待运行完成，看到绿色对勾表示编译成功。
6. 打开本次运行记录。
7. 在页面下方的 **Artifacts** 区域下载：

```text
LogoBatchTool-macOS
```

8. 下载后解压，得到：

```text
批量加Logo工具.app
```

9. 双击 `批量加Logo工具.app` 即可运行。

### macOS 安全提示

由于该 `.app` 没有经过 Apple Developer 签名，macOS 第一次打开时可能提示“无法验证开发者”。可以尝试以下方式：

1. 在 Finder 中右键点击 `批量加Logo工具.app`。
2. 选择 **打开**。
3. 如果仍然无法打开，到 **系统设置 → 隐私与安全性** 中允许打开。

---

# 使用方式二：下载源码本地运行

如果不想使用 GitHub Actions 在线编译，也可以直接下载源码，在本地运行。

## 1. 下载项目源码

可以点击 GitHub 仓库页面的：

```text
Code → Download ZIP
```

下载后解压到本地文件夹。

也可以使用 Git 命令克隆项目：

```bash
git clone https://github.com/MINGYL03/mac-.git
cd mac-
```

---

## 2. 安装 Python 依赖

本项目需要 Python 3，并依赖 Pillow 和 PyInstaller。

依赖文件 `requirements.txt` 内容一般为：

```text
pillow
pyinstaller
```

在项目文件夹中打开终端，执行：

### Windows

```bash
python -m pip install -r requirements.txt
```

如果你的电脑使用 `py` 命令启动 Python，则执行：

```bash
py -m pip install -r requirements.txt
```

### macOS

```bash
python3 -m pip install -r requirements.txt
```

---

## 3. 直接运行源码

### Windows 运行

```bash
python logo_batch_gui.py
```

如果 `python` 命令不可用，可以尝试：

```bash
py logo_batch_gui.py
```

### macOS 运行

```bash
python3 logo_batch_gui.py
```

运行后会打开图形界面。

---

# 使用方式三：下载源码后本地编译

如果希望在自己的电脑上生成独立程序，可以使用 PyInstaller 本地编译。

## 1. Windows 本地编译 exe

在项目文件夹中打开终端，执行：

```bash
python -m PyInstaller --onefile --noconsole --name "批量加Logo工具" logo_batch_gui.py
```

如果使用 `py` 命令，则执行：

```bash
py -m PyInstaller --onefile --noconsole --name "批量加Logo工具" logo_batch_gui.py
```

编译完成后，程序位于：

```text
dist/批量加Logo工具.exe
```

双击该 exe 即可运行。

---

## 2. macOS 本地编译 app

在 Mac 终端中进入项目文件夹，执行：

```bash
python3 -m PyInstaller --windowed --name "批量加Logo工具" logo_batch_gui.py
```

编译完成后，程序位于：

```text
dist/批量加Logo工具.app
```

双击该 app 即可运行。

---

# 程序使用说明

1. 启动程序。
2. 点击 **选择照片文件夹**，选择需要批量处理的图片目录。
3. 点击 **选择 Logo 图片**，选择要添加的 Logo / 水印图片。
4. 点击 **选择输出文件夹**，选择处理后图片的保存位置。
5. 调整 Logo 宽度、透明度、水平位置和垂直位置。
6. 也可以直接在右侧预览图中拖动 Logo。
7. 选择输出格式，例如保持原格式、JPG 或 PNG。
8. 点击 **开始批量加 Logo**。
9. 等待处理完成，输出图片会保存在指定输出文件夹中。

---

# 常见问题

## 1. 运行时报错：No module named PIL

说明没有安装 Pillow。请执行：

### Windows

```bash
python -m pip install pillow
```

### macOS

```bash
python3 -m pip install pillow
```

---

## 2. GitHub Actions 中找不到在线编译任务

请检查 workflow 文件是否位于：

```text
.github/workflows/
```

例如：

```text
.github/workflows/mac-build.yml
.github/workflows/build-windows.yml
```

不要把 `.yml` 文件直接放在仓库根目录，否则 GitHub Actions 不会识别。

---

## 3. 修改 workflow 文件名会影响在线编译吗？

不会。workflow 文件名可以修改，例如：

```text
.github/workflows/main.yml
.github/workflows/mac-build.yml
.github/workflows/build-windows.yml
```

只要文件仍然位于 `.github/workflows/` 文件夹中，GitHub Actions 就可以识别。

Actions 页面左侧显示的名称主要由 yml 文件中的 `name:` 字段决定，例如：

```yaml
name: build macOS app
```

---

## 4. Windows 生成的 exe 能在 macOS 上运行吗？

不能。Windows 的 `.exe` 只能在 Windows 上运行；macOS 的 `.app` 需要在 macOS 环境中编译。

如果你没有 Mac，可以使用本项目的 GitHub Actions 在线编译 macOS 版本。

---

## 5. macOS 提示无法打开 app 怎么办？

这是因为应用没有 Apple Developer 签名。可以尝试：

1. 右键点击 app。
2. 选择 **打开**。
3. 如果仍然无法打开，到 **系统设置 → 隐私与安全性** 中允许打开。

---

## 6. Windows 杀毒软件提示风险怎么办？

PyInstaller 打包的单文件 exe 有时会被杀毒软件误报。如果担心，可以选择：

1. 下载源码后本地运行。
2. 下载源码后本地编译。
3. 使用 `--onedir` 文件夹模式重新打包。

---

# 依赖环境

* Python 3.9 或以上版本
* Pillow
* PyInstaller
* Tkinter

说明：Tkinter 通常随 Python 一起安装。如果运行界面时提示 Tkinter 相关错误，请重新安装完整版本 Python。

---
