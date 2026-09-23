> Repository publication copy: internal links were relocated; original source hashes are in `provenance.json`. Recorded measurements and conclusions are unchanged.

# GEO 首轮工程产物复核

版本：**GEO-REVIEW-R1**；日期：2026-09-22（北京时间）；复核者：角色 01。对象：角色 02 的 `GEO-ENGINEERING-R1 / run-02`。状态：**P0 工程证据复核通过；研究验证场景数仍为 0**。

## 结论与范围

保存的配置、运行日志、原始张量和导出产物相互吻合，支持在 RTX 4060 Laptop 上成功完成一例真实双图推理并保存可检查结果。未发现需要阻止当前工程结论的证据冲突。这里的“通过”是对已保存产物及解释的一致性复核，没有第二次运行模型、重建环境或独立测量几何真值。

本次遵循 lab-report 技能的证据与结果口径要求。工程执行按 **GEO-P0.1**；当前 **GEO-P0.2** 仅用于工程验收兼容性与解释边界复核，研究 performance 的 `evaluated_under` 仍为 null，不追认新版预注册。H1/H2/H3、原生几何置信度 G0、VGGT 与修复对照均未评估。

## 输入、实现与证据入口

- 02 正式交接（历史内部交接）与工程主报告（本地原始产物：`round1/README.md`）。输入是 Middlebury Motorcycle 左右图，经 scikit-image 固定发行 commit 获取；2 张 741×500，模型实际预处理为 518×336，顺序左→右。
- 实际配置（本地原始产物：`round1/run-02/config.json`）：MapAnything Apache，源码 `3d10cf7a3016fc0f9bb13a071ee66c47b10be0d9`；模型 revision `00f9c245bbcb60522d1ed7f9e9d88462c6e3f38a`；BF16、memory-efficient、minibatch=1、seed=0。原始预测 `apply_mask=False`、confidence mask=False、multiview confidence=False。
- [运行入口源码](../scripts/motorcycle/run_baseline.py)和[导出逻辑](../scripts/motorcycle/export_replay.py)已只读核对。计时先严格加载权重并同步 GPU，再预处理图像；推理计时覆盖 `model.infer` 到 GPU 同步。原始数组先落盘，再对同一次结果应用原生展示掩码，没有第二次 forward。
- [协议关系记录](../records/motorcycle/protocol-alignment.json)以及保存的两版协议，均与角色 01 的 P0.1 快照/P0.2 当前文件逐字节一致。

## 实际复核与量化结果

本次使用本机 Python/NumPy 在 CPU 上读取文件，没有执行 02 的推理脚本。机器可读证据：[REVIEW_R1.json](REVIEW_R1.json)，包含检查范围、25 个文件的实测 hash、数组统计与单位换算。源交付 manifest 的 SHA256 为 `e47d765fdeaa041bbe3f45f2dd767b25d3f721cc61d510179bc0f74b4d8f0613`。

| 检查项 | 01 的实际检查结果 | 可支持的解释 |
| --- | --- | --- |
| 产物一致性 | 25 个关键文件的 SHA256 与 byte size 全部匹配 02 清单；覆盖输入、两份 raw/两份 display NPZ、run-02 产物、配置/资源、选定日志、脚本与协议快照 | 保存结果与此次声明的交付版本吻合；不是对全部 849 个文件逐一复核 |
| 原始预测 | 用 `allow_pickle=False` 加载；两视图 camera/intrinsics/conf/depth/points 全部有限，原始深度各 174,048 个像素均为正 | 输出可读取且基本数值有效，不能由有限数推出正确几何 |
| 相机矩阵 | 末行符合齐次变换，旋转 determinant≈1，`RᵀR-I` 最大绝对偏差分别约 2.58e-11、5.96e-8 | 位姿格式自洽；没有外部参考位姿误差评估 |
| 原始与展示关系 | 两视图 conf 逐元素完全一致；展示 mask 内 depth/pts3d 与原始值逐元素完全一致 | 保留 learned conf，展示未改写有效点几何 |
| 展示掩码 | 左/右保留 148,914 / 148,936；展示深度零值 25,134 / 25,112；原始像素共 348,096 | 总保留 297,850，比例 85.5655%；这是模型掩码保留比例，不是正确率或参考覆盖率 |
| GLB | 独立解析 GLB v2 header/JSON/accessor，POINTS primitive 合计 297,850 | 导出点数精确吻合展示掩码；未把 GLB 坐标与原始相机直接混算 |
| 资源 | 重算 38 个原始采样：整卡峰值 7,780 MiB，进程 RSS 峰 9,298,391,040 bytes | 采样摘要正确；约1秒采样可能漏掉瞬时峰值 |
| 视觉与 RRD | 实际查看 `diagnostics.png`、`viewer-web.png`；图表标注 engineering smoke、未验几何精度、confidence非概率。02 的 `rrd verify` 日志记录1个文件无错误 | 截图展示真实保存结果且声明范围恰当；01 未重新启动 viewer或复做拖动交互 |

原始置信度范围左 `[1, 9.552864]`、右 `[1, 8.399891]`，明显不是 0–1 正确概率。图中深度黑边/零值含显示掩码的作用，不能解释为原模型在这些像素没有输出深度。上游 GLB 导出有 X 轴 180° 坐标变换；相机/深度精度评估应使用 NPZ 的 OpenCV cam-to-world 定义。

### 成本口径

下列为 02 一次成功冷启动记录的复核，不是 01 重测，也不是重复实验均值。原始来源是 [result.json](../records/motorcycle/result.json)、resources.json（本地原始产物：`round1/run-02/resources.json`）及[成本摘要](../records/motorcycle/cost-summary.json)。

| 量 | 值与限制 |
| --- | --- |
| 模型加载 | 14.087 s，使用已下载本地权重 |
| 推理 | 11.050 s，2图、518×336、BF16、GPU同步；成功推理 n=1 |
| 导出 | 13.651 s，包含原始张量落盘、展示掩码、NPZ/GLB/RRD/图表 |
| 加载开始至收尾 | 39.429 s；含阶段间开销、图像预处理和结束监控等，不能简单等同三段时间之和；不含首次安装/下载和 viewer验收 |
| PyTorch allocated / reserved peak | 7.18823 / 7.69922 GiB；在推理前 reset峰值计数，包含仍驻留的权重；不是整卡采样口径 |
| nvidia-smi 整卡采样峰 | 7,780 MiB，包含桌面等其他进程；相对报告容量 8,188 MiB 当时仅约408 MiB差额，不保证可供下一次模型实际使用 |
| RSS采样峰 | 8.65980 GiB，当前运行进程，不是全部系统内存 |
| 初次准备 | 02记录权重下载567.981 s、依赖安装约268.584 s；安装时长来自日志时间，未在本次重新测量。并行项不可相加作为人工工时 |

因此，双图可运行并不证明四图可运行。后续若由主任务分配 TUM四图，先在同类配置下做容量验收并遵循已定 OOM/预算停止规则，不据此提前扩展 P1/P2。新增服务/API费用 CNY0 是 02 的成本记录；用户主动工时、电费与全流程成本没有完整测量。

## 失败、缺失与可公开范围

- `run-01` 日志确认 psutil 收到 WindowsPath 导致异常，发生在模型加载前；已保存修正后的 str 适配及 `run-02`。不能把这次工程适配失败算作模型几何失败，也不能隐去准备成本。
- 原生桌面 viewer 的失败与 Web viewer 的成功分开保留。01 看过成功截图与录像验证日志，未独立重演 viewer/清洁安装/第二次推理；因此只接受“已有可重放产物与重放入口”，不升级为独立 clean-install 复现成功。
- 01 未重新散列 4.914GB checkpoint或全部源码树；strict加载和与Hub LFS一致的验证属于02记录。本次实测hash的25文件范围见JSON，哈希一致性只支持产物一致性。
- 没有 GT、困难场景、pair标签、第二模型、G0或修复差分。研究验证场景=0，H1/H2/H3仍待测，不能给出高置信错误、诊断增益或修复收益结论。
- 原始 Middlebury 照片再分发条款未核清；输入、带照片图表及点云截图维持本地核验范围。这里不新增许可判断或公开上传。

官网可用原创文字：**2026-09-22，在 RTX 4060 Laptop 8 GiB 设备上完成 MapAnything Apache 的一例真实双图工程运行。两张输入预处理至518×336，单次推理11.05秒，并保留可检查输出与录像。工程状态为“原型可运行”；几何精度、消歧和修复效果尚未验证。** 若使用显存指标必须保留 allocated/reserved/整卡采样区别；若使用85.57%只称展示掩码保留比例。本报告不要求官网展示这个对读者价值有限的比例。

## 后续与复核入口

本次接受 P0 交付；P1/P2继续未启动。复核期间主任务已在共同简报（历史内部交接）另行分配02执行P0.2首个TUM四帧窗口：45分钟墙钟、5分钟GPU、0.6GB新数据上限；标准518最多一次，OOM时仅允许预先登记且上游支持的392同四帧fallback。只评六对参考R/t，不取后两窗口、不构成H2校准。该分配不是本报告已完成结果；01不运行GPU，也不修改02源目录。

复查方法：用 `REVIEW_R1.json.checked_files` 的相对路径重新计算 SHA256/大小；NumPy无pickle读取两个 raw/display pair，比较 conf 和mask内 depth/pts3d，统计有限值与有效像素；按GLB accessor求POINTS数量；从resources原始行重算GPU/RSS峰值；对照两个协议快照。这是CPU文件复核，不需要恢复模型环境。真实推理与viewer命令由02主报告维护，不复制成另一套执行入口。
