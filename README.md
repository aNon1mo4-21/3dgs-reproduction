# 3dgs-reproduction
Reproduction of the official 3D Gaussian Splatting pipeline, with documented setup, experiments, and novel-view rendering results.

## 当前进度

环境检查与接入说明见 [docs/day1-environment.md](docs/day1-environment.md)。本机为 Intel 核显，尚未训练或渲染；GPU 运行环境待确定。

官方实现固定在 `third_party/gaussian-splatting`，版本记录见 `records/upstream-versions.txt`。克隆本项目后，仅准备训练所需源码：

```bash
git submodule update --init third_party/gaussian-splatting
git -C third_party/gaussian-splatting submodule update --init --recursive submodules/diff-gaussian-rasterization submodules/simple-knn submodules/fused-ssim
```

可选 SIBR 查看器不属于当前里程碑。
