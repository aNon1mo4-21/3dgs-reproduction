# 环境检查与官方实现接入（2026-09-10）

## 实测结论

- 主机：Windows 11 家庭版，版本 10.0.26200；物理内存 16888094720 字节（约 15.73 GiB）。
- Windows 检测到的显卡：Intel Iris Xe Graphics；未检测到 NVIDIA 显卡。
- Windows PATH 中没有 nvidia-smi、nvcc、conda。
- Python：3.14.0，C:/Python314/python.exe。
- PyTorch：2.9.1+cpu；torch.version.cuda=None；torch.cuda.is_available()=False。
- WSL：Ubuntu-24.04 正在运行，WSL2；另有未启动的 Ubuntu-22.04。
- Ubuntu-24.04：内核 6.6.87.2-microsoft-standard-WSL2；Python 3.12.3；g++ 可用；PATH 中未找到 conda、nvcc、nvidia-smi。尚未检查 WSL 的 PyTorch。
- Git：2.52.0.windows.1。
- GitHub 直连失败；使用系统现有本地代理后克隆成功，期间出现一次连接失败，重试成功。未修改全局 Git 配置。

本机尚不满足官方训练/CUDA 渲染环境；未安装训练依赖，未下载场景，未训练或渲染。GPU 服务器仍待确定。

## 已执行的关键命令

Windows PowerShell：

```powershell
Get-CimInstance Win32_VideoController | Select-Object Name,AdapterRAM,DriverVersion
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version
Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory
Get-Command python,py,conda,nvidia-smi,nvcc,git -ErrorAction SilentlyContinue
py -0p
python -c "import torch; print('torch=',torch.__version__); print('torch_cuda=',torch.version.cuda); print('cuda_available=',torch.cuda.is_available())"
wsl --list --verbose
wsl -d Ubuntu-24.04 -- bash -lc 'uname -r; command -v python3; python3 --version; command -v conda; command -v nvcc; command -v nvidia-smi; command -v g++; df -h /'
git -c http.proxy=http://127.0.0.1:7890 clone https://github.com/aNon1mo4-21/3dgs-reproduction.git
cd 3dgs-reproduction
git -c http.proxy=http://127.0.0.1:7890 submodule add https://github.com/graphdeco-inria/gaussian-splatting.git third_party/gaussian-splatting
git -c http.proxy=http://127.0.0.1:7890 -C third_party/gaussian-splatting submodule update --init --recursive submodules/diff-gaussian-rasterization submodules/simple-knn submodules/fused-ssim
```

代理地址仅适用于本机；其他机器不要照抄。本文为执行记录摘要，不是完整终端逐字日志。

## 为什么这样组织仓库

third_party/gaussian-splatting 是官方仓库的 Git 子模块。父仓库记录它的精确提交，避免上游更新后实验代码悄悄改变；我们自己的环境记录和实验说明放在父仓库。

SIBR_viewers 为可选交互查看器，本阶段不初始化；它的版本仍由官方仓库记录。实际依赖版本见 records/upstream-versions.txt，减号表示该子模块尚未初始化。

当前固定的是官方现有实现，包含论文发布后的扩展，不应宣称是 2023 年原始代码的逐位复现。后续首跑采用基础配置，并记录实际参数。

## 接下来如何检查 GPU 机器

在选定的 Linux GPU 机器执行以下只读检查，依据输出选择环境：

```bash
nvidia-smi
command -v nvcc && nvcc --version
command -v conda && conda --version
python3 --version
g++ --version
uname -a
df -h .
```

nvidia-smi 检查显卡、显存和驱动；其中的 CUDA Version 不能单独证明安装了相应 CUDA Toolkit。nvcc 才是 CUDA 编译器。PyTorch 自带或依赖的 CUDA 运行时与编译扩展所需 Toolkit 是不同层次。

官方 environment.yml 固定 Python 3.7.13、PyTorch 1.12.1 和 cudatoolkit 11.6；README 同时提及 CUDA SDK 11.8 与 11.6 的已知问题。不要在当前 Python 3.14 全局环境直接执行安装；待 GPU/驱动/编译器确认后，再创建独立环境并记录兼容性调整。

## 与研究内容的联系

3DGS 用许多可优化的三维高斯表示场景。每个高斯有位置、空间形状、透明度和外观参数。渲染器把它们投影到给定相机的图像平面，再按可见性合成颜色。训练时比较渲染结果和真实照片，通过梯度调整参数，因此渲染器需要支持反向传播。

官方 diff-gaussian-rasterization 提供这项可微渲染能力；simple-knn 用于初始化时估计点的邻域尺度；fused-ssim 加速结构相似性计算。这解释了为什么只有 Python 包还不够：核心算子包含需要编译的 CUDA/C++ 代码。

本阶段的成功标准是环境事实清楚、源码版本固定、训练依赖源码到位。它不等于已经复现论文结果。

## What I now understand

待用户用自己的话补充，尚未把解释过的内容视为已经掌握。

## 来源

- https://github.com/graphdeco-inria/gaussian-splatting
- 固定提交中的 README.md、environment.yml、.gitmodules 及源码。
