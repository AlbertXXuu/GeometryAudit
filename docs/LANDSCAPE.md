> Repository publication copy: internal links were relocated; original source hashes are in `provenance.json`. Recorded measurements and conclusions are unchanged.

# GEO 直接竞争核验

版本：GEO-LANDSCAPE-0.1；核验日期：2026-09-22（北京时间）。角色 01；状态：一手资料与公开实现核验完成，本机性能未实测。

本轮问题依据：并行简报第 1、5 节（历史内部交接）登记的 CAND-GEO-01：无序、重复结构输入中，模型置信度与独立估计的几何证据是否互补，能否定位并受控处理错误关系。最低验收是本文件、[可执行协议](PROTOCOL.md)、具体数据入口和角色交接；不以本轮文献调查作为新方法有效性证据。

## 判断

继续一轮有上限的诊断实验有依据；“置信度 + 几何一致性 + 剪边”本身尚不构成新颖性。原生能力、学习式消歧和图剪枝已经覆盖大部分概念空间。当前值得测量的是：在独立标签、同一输入和相同误删约束下，简单组合是否仍提供增量；代价是否低于直接使用现有消歧方法。没有增量时停止新增算法，保留复现与负结果。

## 直接比较

下表的效果均为作者报告；没有将论文数字当作本机结果。“独立几何”指独立估计路径，不能自动升级为正确性真值。

| 方案 | 问题、输入和信号 | 处理与评测 | 公开实现与本轮含义 |
| --- | --- | --- | --- |
| MapAnything | 多视图度量重建；支持 RGB 及可选几何输入，输出位姿、深度、逐像素 `conf` | 原生 `use_multiview_confidence` 使用多视图深度一致性；另有置信度百分位过滤、有效性及非歧义掩码 | [官方仓库](https://github.com/facebookresearch/map-anything)。代码和模型入口可见，已有 VGGT 等适配。原生几何置信度必须入对照；掩码名称不证明能识别物理表面混淆。统一字段不代表置信度跨模型可比 |
| Doppelgangers++（CVPR 2025） | 判断双图是否观察相同物理表面；MASt3R 几何特征加 Transformer 分类器 | 删除低真匹配概率边，接 COLMAP / MASt3R-SfM；报告 pair 分类与重建结果 | [论文/项目](https://doppelgangers25.github.io/doppelgangers_plusplus/)、[代码](https://github.com/doppelgangers25/doppelgangers-plusplus)。权重、COLMAP/MASt3R-SfM 示例公开。是最近的已实现强替代；本机安装、权重读取和成本仍待 02 测量 |
| XDG，arXiv 2608.29733v2，2026-09-04 | DA3 加 LoRA，以 camera token 作双图消歧；包含双顺序聚合 | 在候选匹配图过滤边；DG、VisymScenes 分类及多数据集 SfM 比较，作者报告相对 DG++ 更快 | [论文](https://arxiv.org/html/2608.29733v2)、[代码](https://github.com/xtcpete/xdg)。有 checkpoint 链接及显式 pair-list 推理；用它控制“加一个重分类器”的成本。论文机器、输入规模与本机不同，不移植加速比 |
| Robust Global SfM via View Graph Pruning，2608.22054v1，2026-08-22 | 无序图中的歧义边；局部一致子图、子图重建与跨子图几何 | 跨子图 RANSAC 剪边后再全局重建；包括 books/desk/street/cup、顺序和互联网数据 | [正文 §3–4](https://arxiv.org/html/2608.22054v1)。论文使用 RealityScan 加人工控制点生成参考位姿，并作极线核验；这也是重建参考，不等同外部计量真值。本次未从作者来源确认可运行代码/权重入口；不能记成已复现，更不能用自己写的简单 cycle filter 冒称该方法 |
| DGSfM，2607.09507 | 深度辅助的全局 SfM，同时做图过滤与深度一致性筛选 | [论文摘要](https://arxiv.org/abs/2607.09507)明确覆盖仅极线检查漏过的错误对应 | [作者仓库](https://github.com/sithu31296/DGSfM)本次只有 README，说明代码待发布。作为与组合思路直接重叠的补充反证；当前不要求 02 自行重写整套算法 |

## Streaming 邻近范围

| 工作 | 已核验覆盖 | 与本轮关系、可用性边界 |
| --- | --- | --- |
| [SURE-Map](https://arxiv.org/abs/2609.15795v1)，2026-09-14 | 跨视图几何不确定性与多时间尺度修正；主要针对顺序流中的累积尺度漂移 | 已占据“跨视图 uncertainty 引导修正”的概念；[项目页](https://mingkai-liu.github.io/projects/sure-map/)有代码入口，本轮未执行。顺序流成绩不能替代无序别名场景对照 |
| [Info3R](https://arxiv.org/abs/2609.21938v1)，2026-09-18 | 信息量驱动状态更新，依据更新量与预测置信度触发状态重置 | 长序列在线重建；本轮只核验论文，未确认可运行发行。不能把一般的 confidence-triggered reset 当作空白贡献 |
| [Adaptive World Memory](https://arxiv.org/abs/2609.21502v1)，2026-09-18 | 自适应记忆、时空调节、局部子图与全局优化 | 主要是持久建图/定位/渲染。论文承诺发布；所链 [仓库](https://github.com/dtc111111/AWM-3DFM)本次 Web 请求返回 404，状态为未确认可用 |

## 可复核版本与证据强度

以下 SHA 为 2026-09-22 用 Python 标准库读取 GitHub 官方 API 的默认分支 HEAD。它们用于锁定此次实现核验，不强制覆盖 02 已选版本；02 若使用不同 SHA，需记录差异。网页索引抓取与实际仓库可能不同，以执行时文件为准。

| 仓库 | SHA | 提交时间（UTC） |
| --- | --- | --- |
| facebookresearch/map-anything | `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9` | 2026-08-07 19:34:31 |
| facebookresearch/vggt | `a288dd0f14786c93483e45524328726ab7b1b4ce` | 2026-05-19 03:39:35 |
| doppelgangers25/doppelgangers-plusplus | `f58d86ab6de1ee177ebcabefd444fb86b02297f9` | 2025-04-08 00:16:56 |
| xtcpete/xdg | `7a836c26f6c8950ccc131aa1b002c4747388fe07` | 2026-09-20 23:22:27 |
| cvg/sfm-disambiguation-colmap | `24e4a0db74ac4cbf72e3239920352ec1f06e60ce` | 2024-06-03 09:25:58 |
| sithu31296/DGSfM | `e8e8170285588b1c20d65e164c2d3061ef2afffb` | 2026-07-10 14:52:55 |

代码许可、模型权重许可、数据许可分别记录。GitHub API 对部分仓库返回 NOASSERTION/null，不能据此推断可任意再分发；实际执行时保存对应 LICENSE/模型卡。MapAnything 的 Apache 模型入口与默认权重分开，[VGGT 官方 README](https://github.com/facebookresearch/vggt)也区分原始和 commercial checkpoint。这里没有安装依赖、运行模型、下载权重或数据全集。

## 仍未证实的差异

1. **增量是否存在：** 现有 DG++/XDG 是否已把目标错误全找出；MapAnything 原生多视图置信度是否已足够。全部解决即合并到现有工具使用方案，不维持新算法主张。
2. **置信度到底在评估什么：** 高逐像素分数与某个错误候选边共存，不足以证明模型预测了该错误关系；必须另测位姿/对应本身是否错误。
3. **独立性有多强：** SIFT 的独立双图估计仍可能与基础模型共同被重复纹理误导；两个模型也可能共享训练数据和归纳偏好。外部参考标签才提供正确性检验。
4. **真实任务成本：** 小图筛边可能比一套额外诊断器更便宜；人工核验、匹配、模型加载、下载和失败重试均需入账。
5. **覆盖不够时怎样表述：** 对三场景、第二模型、留出收益及强基线的检查缺一项，结论限定为局部复现/探索证据，不能写普遍有效或原创方法成立。

## 本轮资料访问限制

官方论文、README、数据目录页已核验。PowerShell/curl 的 TLS 访问失败；Python 可读取 GitHub API，但对 TUM/Cornell 数据服务器 HEAD 请求出现证书链错误，因此未确认这两处大文件的本机下载吞吐、压缩包内容和哈希。未关闭证书校验。数据目录中公布的体量是来源声明，协议明确区分“公开入口已确认”与“本机文件已取得”。
