# 3D Gaussian Splatting Reproduction

我在这个仓库中记录官方 3D Gaussian Splatting（3DGS）流程的复现过程，包括环境配置、源码版本、实验命令和结果验证。第一阶段的目标是用一个小型公开多视图场景完成训练，并生成可核验的新视角图像。

## 当前状态

截至 2026-09-10，我已完成源码接入和远端 GPU 基础环境验证，尚未完成官方 CUDA 扩展编译、场景训练或渲染。

- [x] 接入官方实现，固定主仓库及依赖的提交版本。
- [x] 检查本地环境，确认需要远端 CUDA GPU。
- [x] 验证远端 GPU、CUDA 编译器和 PyTorch，并通过 GPU 张量运算检查。
- [x] 将源码与版本记录同步至远端数据盘。
- [ ] 编译官方 CUDA 扩展并验证导入与运行。
- [ ] 准备小型公开场景，记录数据来源和相机划分。
- [ ] 完成训练与留出视角渲染，保存命令、日志及输出。

## 实验环境

| 项目 | 已验证配置 |
| --- | --- |
| GPU | NVIDIA GeForce RTX 4090 D，24564 MiB 显存 |
| 操作系统 | Ubuntu 22.04.1 LTS |
| Python | 3.10.8 |
| PyTorch | 2.1.2+cu118 |
| CUDA Toolkit | 11.8.89 |
| NVIDIA 驱动 | 580.105.08 |
| C++ 编译器 | GCC 11.3.0 |

基础张量运算通过仅表明 PyTorch 能使用 GPU；官方可微光栅化扩展仍需单独编译和验证。详细记录见 [GPU 环境检查](docs/day1-gpu-environment.md)。

## 源码与复现范围

我将 [官方实现](https://github.com/graphdeco-inria/gaussian-splatting) 作为 Git 子模块放在 `third_party/gaussian-splatting`，固定提交为 `54c035f7834b564019656c3e3fcc3646292f727d`。完整依赖版本见 [版本记录](records/upstream-versions.txt)。

该提交包含论文发布后的更新。本阶段旨在跑通固定版本的官方流程；在完成数据划分、参数与指标对齐之前，我不会将结果视为原论文定量结果的严格复现。当前使用的 Python/PyTorch 环境也与官方原始 environment.yml 不同，兼容性以实际编译和运行结果为准。

获取源码：

```bash
git clone https://github.com/aNon1mo4-21/3dgs-reproduction.git
cd 3dgs-reproduction
git submodule update --init third_party/gaussian-splatting
git -C third_party/gaussian-splatting submodule update --init --recursive submodules/diff-gaussian-rasterization submodules/simple-knn submodules/fused-ssim
```

以上命令只获取源码，不安装运行依赖。可选 SIBR 查看器暂不初始化；上游代码适用其自身许可证，见 `third_party/gaussian-splatting/LICENSE.md`。

## 实验记录

- [本地环境检查与源码接入](docs/day1-environment.md)
- [远端 GPU 环境验证](docs/day1-gpu-environment.md)
- [官方实现与子模块版本](records/upstream-versions.txt)

后续我会随实验更新数据来源、运行命令、参数、输出路径和失败记录，使每个阶段的结论都有对应证据。
