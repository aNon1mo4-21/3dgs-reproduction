# 交互式成果展示

我将第一阶段 Truck 实验做成一个独立的静态展示页，让访客先看到实际结果，再按需检查命令和指标。

在线地址：https://truck-3dgs-reproduction.foamy-stoat-2407.chatgpt.site

## 可以验收什么

- 切换全部 32 个留出视角，不按图像质量筛选。
- 拖动分界线对比参考照片与 7,000 步模型渲染，也可单独查看任意一侧。
- 查看当前视角的原始照片编号、PSNR、SSIM。
- 下载原始渲染 PNG、完整逐视角指标和训练/留出划分。
- 比较 1,000 步与 7,000 步的平均指标，查看模型规模、运行记录及备份校验。

## 数据真实性与范围

展示页的 32 张渲染 PNG 和 32 张参考 PNG 提取自已备份的 `truck-7000-artifacts.tar.gz`，没有使用 AI 生成或替代图像。全部渲染 PNG 的 SHA-256 已与实验 `metrics.json` 中的记录核对一致。

页面展示的是预渲染的留出视角结果，不执行在线训练、上传重建或自由相机实时渲染。网站使用静态 HTML/CSS/JavaScript，访问时不需要租赁 GPU。原始实验数据与模型备份仍以 Truck 实验记录为准。

## 本地打开

在仓库根目录运行：

```bash
python -m http.server 8080 --directory showcase
```

浏览器打开 http://localhost:8080 。也可以直接打开 `showcase/index.html`，其数据通过本地脚本加载，不依赖服务端接口。

## 文件组织

- `showcase/index.html`：页面结构。
- `showcase/style.css`：响应式样式。
- `showcase/app.js`：视角选择、对比滑杆和图片下载。
- `showcase/data.js`：对应实验记录的数据快照。
- `showcase/assets/gt/`、`showcase/assets/renders/`：32 对原始 PNG。
- `showcase/metrics.json`、`showcase/dataset.json`：供访客下载的原始实验记录。

在线站点通过 Sites 托管，公开访问；本仓库保留相同的静态页面，便于审阅、下载和迁移。展示页不包含 SSH 凭据或模型归档。

本次完成 JavaScript 语法、静态资源引用和原始渲染图像摘要校验；未进行浏览器自动化交互测试。
