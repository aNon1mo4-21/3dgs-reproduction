#!/usr/bin/env bash
# Run from the repository root on the verified AutoDL base image.
set -euo pipefail
mkdir -p records/build
python -m pip freeze > records/build/base-packages.txt
python -m venv --system-site-packages /root/autodl-tmp/venvs/3dgs
source /root/autodl-tmp/venvs/3dgs/bin/activate
export MAX_JOBS=4
export TORCH_CUDA_ARCH_LIST=8.9
export PIP_CACHE_DIR=/root/autodl-tmp/pip-cache
python -m pip install numpy==1.26.4 ninja==1.11.1.1 plyfile==1.0.3 opencv-python==4.8.1.78 joblib==1.3.2
for mod in diff-gaussian-rasterization simple-knn fused-ssim; do
    python -m pip install --no-build-isolation --no-deps -v "./third_party/gaussian-splatting/submodules/$mod"
done
python -m pip freeze > records/build/resolved-packages.txt
python scripts/check_extensions.py
