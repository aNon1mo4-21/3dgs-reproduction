"""Extract only Truck from the authors' scene archive and record its split."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import zipfile

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'third_party/gaussian-splatting'))
from scene.colmap_loader import read_extrinsics_binary, read_intrinsics_binary, read_points3D_binary
from PIL import Image

archive=Path('/root/autodl-tmp/datasets/tandt_db.zip')
target=archive.parent/'tandt/truck'
target.mkdir(parents=True,exist_ok=True)
extracted=0
with zipfile.ZipFile(archive) as z:
    for item in z.infolist():
        parts=PurePosixPath(item.filename).parts
        if 'truck' not in parts or item.is_dir():
            continue
        relative=Path(*parts[parts.index('truck')+1:])
        destination=(target/relative).resolve()
        assert destination.is_relative_to(target.resolve())
        destination.parent.mkdir(parents=True,exist_ok=True)
        with z.open(item) as src,destination.open('wb') as dst:
            shutil.copyfileobj(src,dst)
        extracted+=1
assert extracted
cameras=read_extrinsics_binary(str(target/'sparse/0/images.bin'))
intrinsics=read_intrinsics_binary(str(target/'sparse/0/cameras.bin'))
points,_,_=read_points3D_binary(str(target/'sparse/0/points3D.bin'))
names=sorted(c.name for c in cameras.values())
test=names[::8]
train=[n for n in names if n not in set(test)]
assert set(train).isdisjoint(test)
for name in names:
    assert (target/'images'/name).is_file(),name
with Image.open(target/'images'/names[0]) as im:
    size=im.size
digest=hashlib.sha256()
with archive.open('rb') as f:
    for block in iter(lambda:f.read(8*1024*1024),b''):
        digest.update(block)
result=dict(source_url='https://repo-sam.inria.fr/fungraph/3d-gaussian-splatting/datasets/input/tandt_db.zip',
            archive_sha256=digest.hexdigest(),archive_bytes=archive.stat().st_size,
            scene_path=str(target),extracted_files=extracted,total_images=len(names),
            train_images=len(train),test_images=len(test),initial_points=len(points),
            first_image_size=list(size),camera_models=sorted(set(c.model for c in intrinsics.values())),
            split_rule='Sorted image names, zero-based indices divisible by 8 held out; official --eval; train_test_exp=False.',
            limitation='COLMAP poses and sparse initialization are provided by the authors; SfM was not recomputed using training images alone.',
            train_names=train,test_names=test,
            rendered_index_to_source={f'{i:05d}.png':name for i,name in enumerate(test)})
record=root/'records/truck/dataset.json'
record.parent.mkdir(parents=True,exist_ok=True)
record.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['train_names','test_names','rendered_index_to_source']},indent=2))
