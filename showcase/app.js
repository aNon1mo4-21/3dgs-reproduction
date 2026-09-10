'use strict';
const data = window.EXPERIMENT;
const $ = (id) => document.getElementById(id);
const views = data.final.per_view;
let selected = 0;
const filmstrip = $('filmstrip');
const thumbs = views.map((view, index) => {
  const button = document.createElement('button');
  button.className = 'thumb';
  button.type = 'button';
  button.setAttribute('aria-label', `留出视角 ${index + 1}，原始照片 ${data.dataset.rendered_index_to_source[view.file]}`);
  button.setAttribute('aria-pressed', String(index === 0));
  const img = document.createElement('img');
  img.src = `assets/renders/${view.file}`;
  img.alt = '';
  img.loading = 'lazy';
  img.width = 98; img.height = 55;
  const caption = document.createElement('span');
  caption.textContent = String(index + 1).padStart(2, '0');
  button.append(img, caption);
  button.addEventListener('click', () => selectView(index));
  filmstrip.append(button);
  return button;
});
function selectView(index) {
  selected = (index + views.length) % views.length;
  const view = views[selected];
  const number = String(selected + 1).padStart(2, '0');
  $('image-error').hidden = true;
  $('reference').src = `assets/gt/${view.file}`;
  $('rendered').src = `assets/renders/${view.file}`;
  $('reference').alt = `留出视角 ${number} 的真实参考照片`;
  $('rendered').alt = `7,000 步模型生成的留出视角 ${number}`;
  $('view-count').replaceChildren(document.createTextNode(number + ' '));
  const total = document.createElement('span'); total.textContent = `/ ${views.length}`;
  $('view-count').append(total);
  $('view-name').textContent = `视角 ${number}`;
  $('source-name').textContent = data.dataset.rendered_index_to_source[view.file];
  $('view-caption').textContent = `留出视角 ${number} · 未参与高斯优化`;
  $('psnr').replaceChildren(document.createTextNode(view.psnr.toFixed(2)));
  const unit = document.createElement('small'); unit.textContent = 'dB'; $('psnr').append(unit);
  $('ssim').textContent = view.ssim.toFixed(4);
  $('download').href = `assets/renders/${view.file}`;
  $('download').download = `truck-render-${view.file}`;
  thumbs.forEach((thumb, i) => thumb.setAttribute('aria-pressed', String(i === selected)));
  const thumb = thumbs[selected];
  const left = thumb.offsetLeft - filmstrip.offsetLeft;
  if (left < filmstrip.scrollLeft || left + thumb.offsetWidth > filmstrip.scrollLeft + filmstrip.clientWidth) {
    filmstrip.scrollTo({left: Math.max(0, left - filmstrip.clientWidth / 2), behavior: 'auto'});
  }
}
$('previous').addEventListener('click', () => selectView(selected - 1));
$('next').addEventListener('click', () => selectView(selected + 1));
$('wipe').addEventListener('input', (event) => {
  const value = Number(event.target.value);
  $('viewer').style.setProperty('--split', `${value}%`);
  event.target.setAttribute('aria-valuetext', `左侧参考照片 ${value}%，右侧模型渲染 ${100 - value}%`);
});
document.querySelectorAll('[data-mode]').forEach(button => {
  if (button.tagName !== 'BUTTON') return;
  button.addEventListener('click', () => {
    $('viewer').dataset.mode = button.dataset.mode;
    document.querySelectorAll('button[data-mode]').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
  });
});
['reference','rendered'].forEach(id => $(id).addEventListener('error', () => { $('image-error').hidden = false; }));
$('retry').addEventListener('click', () => selectView(selected));
selectView(0);
