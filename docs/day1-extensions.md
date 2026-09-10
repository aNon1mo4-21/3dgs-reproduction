# CUDA 扩展构建与验证（2026-09-10）

## 目的与环境

我在已验证的 RTX 4090D / Python 3.10.8 / PyTorch 2.1.2+cu118 / CUDA Toolkit 11.8 环境中编译三个官方依赖。源码提交未作修改，版本见 `records/upstream-versions.txt`。

项目环境位于 `/root/autodl-tmp/venvs/3dgs`，使用 `venv --system-site-packages` 复用基础镜像中的 PyTorch。新增包安装在该环境中；这不是完全隔离的环境，复查时需要同时参考基础包清单与最终包清单。两份清单是环境快照，不是跨机器通用的锁文件。

我显式固定 NumPy 1.26.4、ninja 1.11.1.1、plyfile 1.0.3、opencv-python 4.8.1.78 和 joblib 1.3.2，避免安装时无意升级基础计算栈。扩展采用 `--no-build-isolation --no-deps`，在已经选定的 PyTorch 环境中构建。

`TORCH_CUDA_ARCH_LIST=8.9` 对应本次 GPU；`MAX_JOBS=4` 限制编译并发。产物针对当前机器，迁移到不同架构 GPU 时需要重新评估并构建。

## 可执行记录

在仓库根目录运行以下命令。脚本整理自本次实际执行的步骤；其默认路径与基础环境针对本实例。

```bash
mkdir -p records/build
bash scripts/build_extensions.sh > records/build/rebuild.log 2>&1
```

在已安装环境中单独验证：

```bash
source /root/autodl-tmp/venvs/3dgs/bin/activate
python scripts/check_extensions.py
```

## 验证设计

1. **simple-knn**：对固定种子生成的 2048 个三维点，比较 CUDA 算子的最近三个其他点的平均平方距离与 CPU 暴力计算结果。
2. **fused-ssim**：比较融合算子与官方 PyTorch SSIM 实现的标量结果及输入图像梯度。
3. **可微光栅化**：在透视相机前放置一个合成高斯，检查输出图像、可见半径、深度和反向传播梯度；要求颜色与透明度梯度非零。

这些测试验证选定输入上的执行与数值一致性，不覆盖算子的所有边界条件，也不构成真实场景训练、新视角评测或论文指标复现。可微光栅化测试采用预计算 RGB、关闭抗锯齿，尚未覆盖球谐外观及所有可选分支。

## 记录文件

- `records/build/base-packages.txt`：创建项目环境前的基础包快照。
- `records/build/install.log`：实际依赖安装与 CUDA 编译日志。
- `records/build/resolved-packages.txt`：安装后的完整包快照。
- `records/build/check.log`：合成 GPU 验证结果。

## 实测结果

三个扩展均成功构建，安装过程退出码为 0；验证脚本退出码为 0，结果为 PASS。官方 `train.py --help` 与 `render.py --help` 均返回 0，输出分别保存在 `train-help.txt` 和 `render-help.txt`。

| 检查 | 结果 |
| --- | --- |
| KNN 与 CPU 参考值的最大绝对误差 | 3.403984010219574e-7 |
| SSIM 标量绝对误差 | 0.0（本次输入、float32） |
| SSIM 梯度最大绝对误差 | 2.7939677238464355e-9 |
| 合成高斯的投影半径 | 5 像素 |
| 合成图像的最大值 | 0.34646663069725037 |
| 透明度梯度 | 0.0012277357745915651 |

构建过程存在上游编译警告，但没有阻止构建；本次未修改官方源码。安装与测试按步骤执行后，我将命令整理成构建脚本，尚未在全新实例上从头重放该脚本。

本次结果支持继续进行小场景训练。尚未下载训练场景，也未验证完整优化过程、模型保存和留出视角渲染。
