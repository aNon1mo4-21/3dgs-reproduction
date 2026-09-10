"""Streaming PSNR/SSIM on the official renderer's saved PNGs (no LPIPS)."""
import hashlib
import json
from pathlib import Path
import sys

import torch
from PIL import Image, ImageDraw
import torchvision.transforms.functional as TF

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'third_party/gaussian-splatting'))
from utils.loss_utils import ssim
from utils.image_utils import psnr

stage=sys.argv[1]
iteration=1000 if stage=='smoke' else 7000
model=Path('/root/autodl-tmp/outputs')/('truck_'+stage)
folder=model/'test'/f'ours_{iteration}'
record=root/'records/truck'/stage
files=sorted((folder/'renders').glob('*.png'))
assert files
dataset=json.loads((root/'records/truck/dataset.json').read_text())
assert len(files)==dataset['test_images']
rows=[]
with torch.no_grad():
    for file in files:
        gt=folder/'gt'/file.name
        a=TF.to_tensor(Image.open(file).convert('RGB')).cuda()
        b=TF.to_tensor(Image.open(gt).convert('RGB')).cuda()
        assert a.shape==b.shape and torch.isfinite(a).all()
        rows.append(dict(file=file.name,psnr=psnr(a.unsqueeze(0),b.unsqueeze(0)).item(),ssim=ssim(a,b).item(),
                         render_sha256=hashlib.sha256(file.read_bytes()).hexdigest()))
result=dict(views=len(rows),psnr_mean=sum(r['psnr'] for r in rows)/len(rows),
            ssim_mean=sum(r['ssim'] for r in rows)/len(rows),
            protocol='Mean of per-view metrics on saved RGB PNGs; official PSNR and SSIM functions; LPIPS not computed.',
            per_view=rows)
(record/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
# Deterministic views for inspection, not selected by score.
selected=[0,len(files)//2,len(files)-1]
width=480
canvas=Image.new('RGB',(2*width,3*(270+30)),(245,245,245))
draw=ImageDraw.Draw(canvas)
for row,index in enumerate(selected):
    file=files[index]
    for col,kind in enumerate(['gt','renders']):
        im=Image.open(folder/kind/file.name).convert('RGB')
        im.thumbnail((width,270))
        y=row*300
        draw.text((col*width+8,y+8),f'{kind}: {file.name}',fill=(0,0,0))
        canvas.paste(im,(col*width,y+30))
canvas.save(record/'comparison.jpg',quality=92)
print(json.dumps({k:v for k,v in result.items() if k!='per_view'},indent=2))
