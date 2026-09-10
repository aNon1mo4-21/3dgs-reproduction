# Truck：从多视图图像到留出视角渲染

## 实验问题

我希望验证固定版本的官方 3DGS 实现能否从公开场景的图像、相机参数和稀疏点云出发，完成高斯优化、模型保存和留出视角渲染。这个实验是第一阶段流程复现，不是原论文默认 30,000 步配置的定量复现。

## 数据与划分

数据来自作者项目页链接的 [Tanks and Temples / Deep Blending 场景包](https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip)。本次只解压 Truck 场景，原始场景来自 Tanks and Temples。

- 压缩包大小：682,628,995 字节。
- SHA-256：`816e62f22a161abbfe841d2a6b10cdf036e297c9fa289b3bfeee9c6ec5226d7e1`，这是本次下载后记录的摘要，不是与作者发布的独立校验值比对的结果。
- 总图像数：251；训练图像：219；留出图像：32。
- 初始点云：136,029 点；相机模型：PINHOLE。
- 首张源图像：979 × 546；本次 `-r 2`，首张实际渲染输出为 490 × 273。
- 划分采用官方 `--eval`：对图像名排序，将零起始索引能被 8 整除的图像留出；`train_test_exp=False`。

留出照片不参与高斯优化；相机参数和初始点云由作者提供，未重新使用训练图像单独运行 SfM。因此这里验证的是固定 COLMAP 初始化下的留出视角表现。完整文件名及渲染编号映射见 `records/truck/dataset.json`。

## 配置与执行

使用已验证的 RTX 4090D / PyTorch 2.1.2+cu118 / CUDA 11.8 环境。官方源码与子模块均不修改。

| 阶段 | 迭代次数 | 初始化 | 目的 |
| --- | --- | --- | --- |
| smoke | 1,000 | 作者提供的稀疏点云 | 验证训练、保存、重新加载和渲染 |
| 7000 | 7,000 | 从同一稀疏点云独立开始 | 形成第一阶段训练结果 |

两次运行均使用 `--eval -r 2 --disable_viewer`，在最后一步评估、保存 PLY 模型和训练检查点。其余优化参数使用固定提交的默认值；包括最高球谐阶数 3、默认优化器和增密规则。7,000 步运行不是从 smoke 检查点继续训练，也不代表已经充分收敛。

代码中的位置学习率调度最大步数仍为默认 30,000；本次没有把整个默认调度压缩成 7,000 步。未提供深度输入，未开启抗锯齿或 `train_test_exp`。

实际命令及每个进程的耗时、退出码保存于各阶段的 `run.json`；完整 stdout/stderr 分别在 `train.log` 和 `render.log`。后台启动使用 nohup，以避免 SSH 断开终止任务。

```bash
source /root/autodl-tmp/venvs/3dgs/bin/activate
mkdir -p /root/autodl-tmp/datasets
curl -L --fail --retry 3 --connect-timeout 20 \
  https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip \
  -o /root/autodl-tmp/datasets/tandt_db.zip
python scripts/prepare_truck.py
python scripts/run_truck.py smoke
python scripts/evaluate_truck.py smoke
# 确认短程训练及输出通过后，再执行：
python scripts/run_truck.py 7000
python scripts/evaluate_truck.py 7000
```

数据在 `/root/autodl-tmp/datasets/tandt/truck`，模型与完整渲染结果在 `/root/autodl-tmp/outputs/truck_smoke` 和 `/root/autodl-tmp/outputs/truck_7000`。

## 评估含义

我对官方 `render.py` 保存的 RGB PNG 逐视角计算官方 PSNR、SSIM，然后取 32 个视角的算术平均。PNG 量化会使这些值与训练日志中浮点渲染的在线评估略有差异。未计算 LPIPS。

PSNR 反映逐像素重建误差，越高越好；SSIM 比较局部亮度、对比度和结构，越接近 1 越好。两项指标都不能替代视觉检查，也不能证明任意相机轨迹下都没有伪影。

对比图按固定编号选择第一个、中间和最后一个留出视角，没有按指标挑选最好看的视角。左列为对应参考照片，右列为渲染结果。

## 当前阶段的边界

本次使用作者准备的相机参数与点云，尚未验证从自己的原始照片运行 COLMAP。单场景、降低分辨率、7,000 步及更新后的官方源码配置，均限制了与论文表格直接比较的有效性。

## 调试记录

下载后预览 ZIP 文件列表时，命令通过 `head -25` 截断输出，导致 Python 列表进程报告 BrokenPipeError。错误发生在列表打印阶段，下载已完成；随后 Truck 文件解压、图像/相机对应检查及训练均通过。原始下载与列表输出保存在 `records/truck/download.log`。

离线评估脚本第一次调用 PSNR 时缺少批次维度，将 `3×H×W` 输入传给按批次处理的函数，得到三个值，随后 `.item()` 报错。我将 PSNR 输入改为 `1×3×H×W`，重新执行通过。初始错误保存在 `records/truck/smoke/evaluate-initial-error.log`；官方训练与渲染未受影响。

## 实测结果

| 阶段 | 训练进程耗时 | 渲染进程耗时 | 留出 PSNR | 留出 SSIM |
| --- | --- | --- | --- | --- |
| 1,000 步 | 32.13 秒 | 19.62 秒 | 22.082894 dB | 0.812084 |
| 7,000 步 | 114.04 秒 | 17.36 秒 | 25.145932 dB | 0.906286 |

以上耗时包含对应 Python 进程的启动、数据加载与保存，不包含下载、环境构建和离线评估；不是实时渲染 FPS。四个训练/渲染进程均退出 0，两阶段均产生 32 张留出视角图像。

7,000 步模型包含 1,032,308 个高斯，PLY 为 256,013,916 字节，训练检查点为 748,149,666 字节。PLY 保存用于渲染的高斯属性；训练检查点另包含优化所需状态，具体恢复能力受该版本官方实现约束。

视觉检查中，7,000 步结果的车身、轮胎、木板和背景边缘较短程结果清晰，仍可见地面和近景局部模糊、细结构及背景伪影。指标提升支持本次训练有效，但不说明已充分收敛。

![Reference on left, 7000-step render on right](../records/truck/7000/comparison.jpg)

## 产物与备份

完整输出在服务器 `/root/autodl-tmp/outputs/truck_7000`，包含 PLY、训练检查点、相机/配置、TensorBoard 日志以及 32 对参考/渲染 PNG。仓库只保存轻量日志、指标、映射和对比图，完整模型单独备份。

完整归档已下载到本地仓库旁的 `truck-7000-artifacts.tar.gz`，大小 870,669,378 字节。本地 SHA-256 与服务器一致，归档目录读取通过；校验记录见 `records/truck/7000/backup.json` 和 `archive.sha256`。

服务器打包命令：

```bash
tar -czf /root/autodl-tmp/truck-7000-artifacts.tar.gz -C /root/autodl-tmp/outputs truck_7000
sha256sum /root/autodl-tmp/truck-7000-artifacts.tar.gz
```

原始数据可由官方链接重新获取；模型归档不包含原始数据集。重新渲染时需准备数据并按实际路径覆盖 `-s`，因为 `cfg_args` 中记录的是本次服务器路径。

## 本次产物对应的流程

1. `images/` 是观测照片；它们提供训练时的颜色监督。
2. `sparse/0/cameras.bin` 和 `images.bin` 保存相机内参与各图像的位姿，使照片像素能与三维空间关联。
3. `points3D.bin` 提供初始三维点，官方加载器首次运行时转换为 PLY；这些点用于初始化高斯，不是训练后的场景模型。
4. `train.py` 反复从训练相机渲染图像，通过颜色/结构误差更新高斯，并执行增密和裁剪。
5. `point_cloud/iteration_7000/point_cloud.ply` 是训练后的高斯表示；`chkpnt7000.pth` 另保存训练状态。
6. `render.py` 重新加载模型，在留出相机位姿处生成 `test/ours_7000/renders/*.png`；对应的 `gt/*.png` 用于评估，不是渲染器的逐像素输入。
