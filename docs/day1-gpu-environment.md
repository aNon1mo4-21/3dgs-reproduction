# GPU 实例检查（2026-09-10）

SSH 连接成功。下列结果来自实例实际执行，不来自租赁页面。

- Ubuntu 22.04.1 LTS；18 核 CPU、60GB 内存（登录横幅）。
- NVIDIA GeForce RTX 4090 D；24564 MiB 显存；Compute Capability 8.9。
- 驱动 580.105.08；nvidia-smi 显示 CUDA 13.0。
- nvcc 11.8.89；Python 3.10.8；PyTorch 2.1.2+cu118。
- torch.cuda.is_available(): True。
- GPU 运算 `(torch.ones(3,device='cuda')*2).cpu()` 返回 tensor([2., 2., 2.])。
- g++ 11.3.0；Git 2.34.1；Conda /root/miniconda3/bin/conda。
- 系统盘 30GB，检查时约 30GB 可用；/root/autodl-tmp 数据盘 50GB，检查时约 50GB 可用。

结论：基础 GPU 环境可用。尚未验证官方 CUDA 扩展编译、训练或渲染。

核心检查命令：

```bash
nvidia-smi
nvcc --version
python --version
python -c "import torch; print(torch.__version__,torch.version.cuda,torch.cuda.is_available()); print(torch.cuda.get_device_name(0)); print(torch.cuda.get_device_capability(0)); print((torch.ones(3,device='cuda')*2).cpu())"
g++ --version
df -h / /root/autodl-tmp
```

官方源码从本地完整仓库打包传输（含 Git 元数据及已初始化子模块），无需重新选择上游版本。传输归档位于仓库之外。凭据不纳入记录。
