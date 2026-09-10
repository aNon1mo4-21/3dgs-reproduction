"""Run a documented stage with the unmodified official train/render entrypoints."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('stage', choices=['smoke', '7000'])
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
source = Path('/root/autodl-tmp/datasets/tandt/truck')
model = Path('/root/autodl-tmp/outputs') / ('truck_' + args.stage)
record = root / 'records/truck' / args.stage
record.mkdir(parents=True, exist_ok=True)
steps = 1000 if args.stage == 'smoke' else 7000
commands = [
    [sys.executable, str(root/'third_party/gaussian-splatting/train.py'),
     '-s', str(source), '-m', str(model), '--eval', '-r', '2',
     '--iterations', str(steps), '--test_iterations', str(steps),
     '--save_iterations', str(steps), '--checkpoint_iterations', str(steps),
     '--disable_viewer'],
    [sys.executable, str(root/'third_party/gaussian-splatting/render.py'),
     '-m', str(model), '--iteration', str(steps), '--skip_train'],
]
metadata = dict(stage=args.stage, iterations=steps, commands=commands,
                start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                upstream=subprocess.check_output(['git','-C',str(root/'third_party/gaussian-splatting'),'rev-parse','HEAD'],text=True).strip(),
                status='running', steps=[])
path = record/'run.json'
def save():
    path.write_text(json.dumps(metadata, indent=2)+'\n')
save()
for name, command in zip(['train', 'render'], commands):
    start = time.monotonic()
    with (record/(name+'.log')).open('w') as log:
        result = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT,
                                env={**os.environ, 'PYTHONUNBUFFERED':'1'})
    metadata['steps'].append(dict(name=name, returncode=result.returncode,
                                 wall_seconds=time.monotonic()-start))
    if result.returncode:
        metadata['status']='failed'
        save()
        sys.exit(result.returncode)
    save()
renders = sorted((model/'test'/f'ours_{steps}'/'renders').glob('*.png'))
assert renders, 'No held-out renders produced'
metadata.update(status='complete', rendered_views=len(renders),
                end_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
save()
