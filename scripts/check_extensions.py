"""Synthetic CUDA checks; these are not a trained-scene reproduction."""
import json
import math
from pathlib import Path
import sys

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'third_party/gaussian-splatting'))
from diff_gaussian_rasterization import GaussianRasterizer, GaussianRasterizationSettings
from simple_knn._C import distCUDA2
from fused_ssim import fused_ssim
from utils.graphics_utils import getProjectionMatrix
from utils.loss_utils import ssim

torch.manual_seed(42)
assert torch.cuda.is_available()
results = {'torch': torch.__version__, 'gpu': torch.cuda.get_device_name(0)}

# Compare the CUDA mean squared distance to the nearest three OTHER points
# against a brute-force CPU reference, including more than one spatial box.
points = torch.rand(2048, 3)
distances = torch.cdist(points, points).square()
distances.fill_diagonal_(float('inf'))
expected = distances.topk(3, largest=False).values.mean(1)
actual = distCUDA2(points.cuda()).cpu()
torch.testing.assert_close(actual, expected, atol=2e-6, rtol=2e-4)
results['knn_max_abs_error'] = (actual - expected).abs().max().item()

# Compare both SSIM value and image gradient with the upstream PyTorch path.
a = torch.rand(1, 3, 32, 32, device='cuda', requires_grad=True)
b = torch.rand_like(a)
fast = fused_ssim(a, b)
reference = ssim(a, b)
fast_grad = torch.autograd.grad(fast, a, retain_graph=True)[0]
ref_grad = torch.autograd.grad(reference, a)[0]
torch.testing.assert_close(fast, reference, atol=2e-5, rtol=2e-4)
torch.testing.assert_close(fast_grad, ref_grad, atol=2e-5, rtol=2e-3)
results['ssim_abs_error'] = (fast - reference).abs().item()
results['ssim_gradient_max_abs_error'] = (fast_grad - ref_grad).abs().max().item()

# One visible Gaussian, perspective camera, RGB appearance and a black background.
view = torch.eye(4, device='cuda')
projection = getProjectionMatrix(0.01, 100, math.pi/2, math.pi/2).T.cuda()
settings = GaussianRasterizationSettings(
    image_height=32, image_width=32, tanfovx=1., tanfovy=1.,
    bg=torch.zeros(3, device='cuda'), scale_modifier=1., viewmatrix=view,
    projmatrix=projection, sh_degree=0, campos=torch.zeros(3, device='cuda'),
    prefiltered=False, debug=False, antialiasing=False)
means = torch.tensor([[0., 0., 2.]], device='cuda', requires_grad=True)
screen = torch.zeros_like(means, requires_grad=True)
color = torch.tensor([[0.8, 0.2, 0.1]], device='cuda', requires_grad=True)
opacity = torch.tensor([[0.5]], device='cuda', requires_grad=True)
scale = torch.tensor([[0.15, 0.15, 0.15]], device='cuda', requires_grad=True)
rotation = torch.tensor([[1., 0., 0., 0.]], device='cuda', requires_grad=True)
image, radii, depth = GaussianRasterizer(settings)(
    means3D=means, means2D=screen, opacities=opacity, colors_precomp=color,
    scales=scale, rotations=rotation)
assert image.shape == (3, 32, 32) and radii.item() > 0
assert torch.isfinite(image).all() and image.max() > 0
assert torch.isfinite(depth).all()
image.square().mean().backward()
for name, value in [('means', means), ('screen', screen), ('color', color),
                    ('opacity', opacity), ('scale', scale), ('rotation', rotation)]:
    assert value.grad is not None and torch.isfinite(value.grad).all(), name
assert color.grad.abs().sum() > 0 and opacity.grad.abs().sum() > 0
torch.cuda.synchronize()
results.update(raster_radius=radii.item(), raster_max=image.max().item(),
               opacity_gradient=opacity.grad.item(), status='PASS')
print(json.dumps(results, indent=2))
