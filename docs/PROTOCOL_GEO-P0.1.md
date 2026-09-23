> Repository publication copy: internal links were relocated; original source hashes are in `provenance.json`. Recorded measurements and conclusions are unchanged.

# GEO 最小实验协议

版本：**GEO-P0.1**；制定日期：2026-09-22（北京时间）；状态：可交接的执行规范，尚无按本协议产生的研究结果。协议、阈值、场景切分在查看相应留出结果前冻结。执行前保存本文件 SHA256；更改则递增版本，并保留旧版本及旧运行关系。

依据：并行简报角色 01（历史内部交接）、[竞争核验](LANDSCAPE.md)。资源线索为 02 本轮消息：RTX 4060 Laptop 8188 MiB、桌面约占 1.6 GiB、D 盘余量约 272 GiB；这是 02 的实测回报，执行前由 02 再核对。GPU 与实验目录归 02；01 只维护判据与解释。

## 1. 问题、输出和最小顺序

**H1（诊断）：** 在独立标注的物理表面混淆上，像素置信度代理 C 与另一路图像几何信号 G 的固定组合，能否在同一误报约束下优于最好单信号与现有消歧器？

**H2（几何失败）：** 基础模型是否在至少三个独立物理场景中出现外部参考确认、但 C 未报警的同类位姿/关系错误；VGGT 能否复核其中的失败类型？

**H3（修复）：** 仅在 H1/H2 有实证后，使用已有 SfM 管线剪边，是否减少错误而保持视图和几何完整性？

三个问题分别计分。双图真假标签用于 H1；其本身不能证明完整重建正确、模型位姿错误或修复成功。

| 阶段 | 执行内容 | 最小验收与停点 |
| --- | --- | --- |
| P0 工程 | 已有上游普通场景 2–3 张；随后 TUM fr1/xyz 的固定 4 张 RGB | 输入/版本/命令/原始输出/成本可重放；若有 GT 再验位姿。只有工程跑通也允许交付，明确尚无研究判断 |
| P1 关系诊断 | DG 发布测试数据按物理场景分校准/留出；每次只输入一对图；MapAnything C、原生 G0、独立估计 G、组合、DG++、XDG | 有可信双图标签与场景隔离，产生完整逐对分数。P0 未通过不安装更多模型；强基线缺失时不作胜出结论 |
| P2 几何与修复 | 小规模 4–8 图场景；外部 GT 位姿或盲审物理身份；VGGT；固定 SfM 剪边重建 | 三个独立场景同类错误和第二模型复核作为扩展门槛；有资源、有可靠标签才执行。不为凑失败扩大无限搜索 |

本轮角色 01 验收是本协议与数据入口交接，不要求 02 在同一轮完成 P1/P2。P1/P2 的预算是建议执行上限，不能挤占 02 已登记的更小额度或替代主任务资源分配。

## 2. 可获得的数据入口与抽样

体量为官方页面标示近似值，下载前核对真实 Content-Length/目录。01 本轮未下载图像。先复用 02 已有合法数据，无法从已选场景取得参考时，工程演示与研究样本分开登记。

| 数据与入口 | 最小使用和依据 | 获取与传播边界 |
| --- | --- | --- |
| **TUM RGB-D `freiburg1_xyz`**：[官方序列页](https://cvg.cit.tum.de/data/datasets/rgbd-dataset/download#freiburg1_xyz)；[压缩包](https://cvg.cit.tum.de/rgbd/dataset/freiburg1/rgbd_dataset_freiburg1_xyz.tgz) | 普通对照；约 0.42 GB。包含 RGB、深度及外部运动捕捉轨迹。先取 4 帧，不把深度/GT 位姿输入模型 | [基准说明及许可](https://cvg.cit.tum.de/data/datasets/rgbd-dataset)：CC BY 4.0（有特别说明时从其规定）。保存作者引用、来源、选帧和处理说明。公开入口可见，本机二进制访问待 02 验证 |
| **Doppelgangers 发布测试集**：[官方数据格式/下载](https://github.com/RuojinCai/doppelgangers/blob/main/data/doppelgangers_dataset/README.md)；[标签元数据](https://doppelgangers.cs.cornell.edu/dataset/pairs_metadata.tar.gz)；[测试图片](https://doppelgangers.cs.cornell.edu/dataset/test_set.tar.gz) | 元数据约 12 MB，完整测试图约 2 GB；先元数据后决定下载。发布行含两路径、`pos=1/neg=0`、SIFT 匹配数。按建筑而非图片划分，优先独立侧面/物理表面身份标签 | 公开研究入口已确认；具体照片继承原始来源许可，不能用代码 MIT 代替图片授权。协议交付链接、索引和哈希；官网暂不用未核清权属的图片。二进制可达性未实测成功 |
| **经典 SfM 歧义场景 books / cup / desk / street**：[维护者整理与来源](https://github.com/cvg/sfm-disambiguation-colmap#datasets)、[官方仓库所链包](https://drive.google.com/file/d/14z33byqiUzO096uKjCe4ZJ2A_gc-R6e1/view) | P2 候选：books 用于校准；cup/desk/street 作为留出候选，各最多 8 图。包大小未确认，先列目录/体量；包内 COLMAP 结果不是 GT | 需核对原作者数据条款和真实物理场景去重。没有可信独立标签只作定性复现，不计 H2 三场景。未知体量不直接下载整包；限制内不可取得就跳过并记录 |
| **ETH3D high-res training**：[官方目录](https://eth3d.ethz.ch/datasets)、[格式与激光参考说明](https://www.eth3d.net/documentation) | P2 有尺度/几何参考的后备。先 courtyard：38 图，原 jpg 约 0.4 GB、scan-eval 约 0.2 GB；最多 8 图。再按需要考虑 delivery_area / electro，不将重复纹理或失败视为已知事实 | 数据首页声明 CC BY-NC-SA 4.0；本地研究与官网图片使用分别审查。`points3D.txt` 和 2D tracks 是图像重建产物，不是激光真值；参考深度对应 distorted 图，不能直接套到 undistorted 图。目录部分 Web 请求不稳定，未实测压缩包 |
| **VisymScenes**：[数据卡](https://huggingface.co/datasets/doppelgangers25/VisymScenes)、[文件目录](https://huggingface.co/datasets/doppelgangers25/VisymScenes/tree/main) | 可后续选 `VisymSite0023` 等论文使用场景；有发布 pair 标签与 GPS 元信息；GPS 不作精确位姿 GT | CC BY 4.0；目录总量 108 GB，各 zip 约 7–13 GB，标签文件约 8.96 MB。当前不满足小规模整包获取上限，列为后备，不要求下载。无按场景小包时停止此入口 |

**TUM 确定选帧（P0）：** 按 `rgb.txt` 时间排序，选择起始时间后 2.0、2.5、3.0、3.5 秒最近帧，最大时间差 0.05 秒、帧不重复；找不到则记录 selection-failed，不能看模型结果后换帧。RGB 与 GT 最近邻差须 ≤0.02 秒；所用工具若插值则保存算法及边界。此序列运动较接近平移，旋转和空间覆盖范围有限，不能代表歧义困难集。

**DG 确定抽样（P1）：**

1. 只读发布 test metadata；按顶层物理地标/建筑归组，合并别名、正反面及同一建筑跨采集数据。同一对象不能跨校准/留出。检查与 DG++/XDG 的发布训练集重叠；该检查不能排除基础模型预训练污染，需报告。
2. 在不读取模型分数的情况下，按场景名 UTF-8 字节序处理。场景内去重无序 pair，去除冲突标签；每类按两条相对路径的字节序选前 6 对，共 12 对。只保留两类各 ≥6 对且来源能支撑物理身份的场景；将排除原因也写清。
3. 前 3 个合格场景作校准，后 3 个作留出，余下不使用；最多 6 场景、72 对、最多 144 张独立图片。场景少于 6 时只做 pilot，不能声称达到留出门槛。具体名称、所有图像 SHA256 与标签在运行前写到 `selection.json`，完成后才能冻结本次数据版本。当前尚未取得二进制元数据，绝不把选择器当作已选出六场景。
4. 这份小集合平衡了正负类，是压力测试；其 precision 不能外推为自然场景误报概率。已发布 test 集被其他论文使用过，不是全新未知测试集；本轮只能控制自身的场景泄漏。
5. 每对输入两图，正向与逆向两种顺序；汇总取两顺序风险的均值，保存差值。与 P2 多视图结果分表。候选先固定再计算分数，不能只评估模型认为容易的 pair。

## 3. 独立正确性依据和未知标签

维护两个不混合的标签列：`surface_label={same,different,unknown}` 和 `pose_label={correct,error,unknown}`。

**物理表面标签：** 首先使用发布的独立身份标签；记录原始 row/图像来源和标注规则。在模型分数不可见时，01 复核每场景至少 2 正+2 负对，核查地标别名、正反侧和照片说明；出现冲突就审查该场景全部标签。仅凭“看起来相似”不能判定不同表面，单靠 GPS 距离也不能排除相机看向同一建筑。无法解决的冲突标 unknown，并报告未知比例和原始分母。

**姿态标签：** 用外部 motion capture 或经核实的扫描对齐参考位姿。全部转换为 OpenCV cam-to-world `T_i`，模型相对变换 `T_ji = inverse(T_j) * T_i`。旋转误差为 `acos(clip((trace(R_hat * R_ref^T)-1)/2,-1,1))`；平移方向误差用相同相机坐标中的有向向量夹角，不取绝对内积来隐藏 180° 反向。参考基线 <0.05 m 或参考噪声足以改变阈值分类时，平移标签为 unknown。

- 初始阈值是本协议的工程容差，不是来源保证：R ≤5° 且有效 t ≤10° 为 correct；R >10° 或有效 t >20° 为 error；其余 unknown。无法判 t 而 R 良好时，仅输出 rotation-correct，不能升成整体 correct。
- H2 的“高置信错误”是 `pose_label=error` 且 C 风险不高于校准集 correct pair 的中位数。若校准没有足够 pose-correct 样本，此判断不可用。H1 的 `different + 高像素置信度` 只叫代理分数漏报，不叫 MapAnything 错误重建。
- metric 平移/深度误差单列；VGGT 的尺度不默认等于米。全局 ATE 同时报 SE(3)（适用于有度量尺度）及 Sim(3) 对齐结果、尺度因子；只用单次全场景对齐，不分组件对齐后再拼成“完整”。2 帧不计算可解释的全局 ATE；4–8 帧需检查退化。

**禁止循环论证：** 同一组全局位姿导出的三条相对边相乘天然闭环；不能用它证明正确。真正的 cycle 诊断只可由分别独立拟合的双图边构成，仍只是诊断特征。BA 残差、点云观感、两个模型相互同意、单次 COLMAP 或 RealityScan 输出均不能独立提供真值。没有扫描/运动捕捉的经典歧义场景，可凭盲审来源证据判物理身份，但不报告未获依据的数值位姿精度。

## 4. 固定信号和强对照

统一把分数写成“越大越可疑”。先用固定图像 SIFT 双向最近邻 ratio=0.8 产生 tentative matches；同一个 pair 的所有方法共享对应坐标，但 DG++/XDG 仍按其原生图片输入。长边缩放和 padding/crop 变换必须记录，置信度采样回到同一像素系；不以待评模型置信度/有效性掩码先筛除低分点。有效 tentative matches <20 的 pair 标 `insufficient-matches`，计为弃权，不能消失于分母。

| 组 | 定义及边界 |
| --- | --- |
| B0 原始结果 | 不过滤的模型预测，以及固定 COLMAP/SfM 原始匹配数据库；保存原始快照 |
| C 模型置信度 | 对每条固定 match 取两端逐像素 confidence 的较小值，对 pair 取第 10 百分位，风险取其负值。MapAnything 使用原始 learned `conf`，VGGT 优先 `depth_conf`；如统一 wrapper 改了来源需记录。保留 raw min/max/分位数、NaN 数和聚合规则；不是 pair 正确概率 |
| G0 原生几何置信度 | MapAnything `use_multiview_confidence=True` 单独运行，沿用相同坐标与聚合，不覆盖 C；记录实际源码的输出变换。它来自同一次重建的深度/位姿，应称自一致性强基线 |
| G 独立估计信号 | 从同一 SIFT 对应独立 RANSAC 拟合 fundamental matrix，使用平方根 Sampson 距离阈值 1.5 像素（缩放后坐标；若 API 返回平方距离则用 2.25）、置信度 0.999、最多 10000 次、seed=0；风险 `1 - inlier_count / tentative_count`。保存实际估计器/API及最终按该距离重算的 inlier 数，不能把另一种库内距离直接当同一阈值。拟合退化/失败为弃权。G 不读取模型深度/位姿，也不是独立 GT；重复结构完全可能通过它 |
| CG 固定组合 | 各模型分别用校准集 empirical CDF 将 C/G 风险归一化为 U_C/U_G；`S=(U_C+U_G)/2`，只这一种权重，不网格搜索。CDF 并列取中秩；留出超界截断为 0/1。任一信号缺失则组合弃权 |
| DG++ | 发布 checkpoint 的真匹配概率 p，风险 1-p；保存 checkpoint hash 与版本；原生阈值 0.8 另列。沿用原生双顺序处理，不再额外平均已对称的内部输出 |
| XDG | 同样用 1-p，沿官方 pair-list 接口；单列端到端及已加载模型推理成本。与 DG++ 共用 pair 集，避免其默认匹配器改变输入造成伪收益 |
| 图剪枝强替代 | Robust Global SfM pruning 必须列为覆盖威胁；作者实现未核实，执行状态 N/A。若目标进入 P2，而仍无法比较它，不声称领先图剪枝方法。已有经典方法可按官方实现作补充，不得更名充当该论文复现 |

G 是刻意选择的低成本可证伪信号；它若过弱，结果只能否定这份最小组合，不能否定所有独立几何信号。新增 rotation-cycle/子图算法需另写假设和版本，不能看过留出后追加并仍称预注册。

**输入与公平性：** C/G0/CG 固定同一 MapAnything checkpoint、图像预处理和 pair context；保存未过滤深度、位姿和置信度。VGGT 第二模型用同一原图，可按模型原生分辨率处理并计成本，分模型校准，不直接比较 raw `conf=0.8`。GT 深度、GT 位姿与 surface 标签只进评估文件，不提供给诊断器。相机内参主实验使用模型/原生未知内参路径；后续已知标定实验必须另列，所有基线同等获益。

## 5. 校准、指标与继续门槛

**阈值冻结：** 在校准场景上，枚举该方法观察分数加 ±∞，选择满足宏平均 true-pair 误删率 ≤5%、且每个校准场景最多误删 1 条的最高错误召回点；并列优先误删少，再阈值更保守。报警规则严格 `risk > threshold`。每场景仅 6 个正例时此门槛实际上要求零误删，必须如实说明分辨率很粗。若无法产生报警，保留“全部保留”的阈值，不降低约束直到出现收益。

**留出报告：** 固定阈值，分别报告逐场景 TP/FP/FN/TN、错误召回、正确边误删率、错误类 AP、弃权率、unknown 比例；宏平均为主，微平均为辅。未知标签不进正确性分母，但列原始总数；有真标签但方法弃权按未发现错误计入端到端召回，且单列覆盖率。所有对照使用同一具有共同有效信号的子集作配对比较，并同时给各自全样本覆盖结果，防止删去难例获胜。无某一类标签的场景不计算该项 AP/召回。

保留像素 confidence 的可靠性只是代理结果：不将它直接画成“正确概率校准曲线”。样本集中错误率被人为平衡，AP、precision 与实际工作流基准率分开说明。

**进入下一轮的探索门槛（全部满足）：**

1. 至少 3 个独立物理场景有独立参考确认的同类错误；同一场景不同帧/顺序/重跑不累加成 3 场景。H2 若未测到，H1 只能支持 pair 审计。
2. VGGT 在至少 2 个上述场景复核失败类型；其余场景也报告，模型共同成功/共同失败都保留。第二模型未运行则门槛未完成。
3. CG 留出宏平均错误召回比 C、G、G0 中最好的一个至少高 **10 个百分点**，同时比可运行的 DG++/XDG 最佳者至少高 **5 个百分点**；每个留出场景正确边误删不超过预设预算。基线无可比较输出则结论是不完整，不把 N/A 当 0。
4. 至少 2/3 留出场景方向一致，无单一场景贡献全部收益；报告分子/分母和每场景差值。阈值固定后失败就失败；这是资源分配门槛，不是统计显著性检验，也不是总体保证。
5. 包含获取、特征、加载、推理、汇总的自动耗时不超过最佳可运行直接竞品的 2 倍；人工核验时间单列。有显著更低成本而等效的路径时，可以向主任务建议“复用”，不能改写成准确率胜出。

72 对压力测试只适合初筛。正例数量不足以估计 1%–5% 的生产误报率；不以零观察误报声称高可靠性。后续若需要置信区间，按场景重采样且说明只有 3 个留出场景的局限，不能把图像对当独立样本制造显著性。

## 6. 受控修复（P2，有门槛才执行）

先限定一个已有 COLMAP/SfM 后端和同一原始数据库；不直接将 MapAnything 像素 mask 解释成可删除的 view-graph edge。若后端无可编辑匹配图，本阶段为不适用，先交诊断结果。

1. 用同一图/同一 matcher 比较不删边、C、G、CG、DG++、XDG；G0 可用于有定义的关系聚合。每方法保存独立数据库副本、被删 pair 清单和配置，原始文件只读。全程相同 mapper/BA 设置、seed 和停止阈值。
2. 从冻结得分最高的超阈值边开始，最多删除原始候选边的 10%（向下取整；少于 10 条则不自动删）。为完整性保护，不删当前连通图的桥；无法满足则输出“无法安全自动处理”，不偷偷换成删图。桥限制会漏掉假桥，需要报告该适用边界。
3. 所有方法均按同一删边预算和同一保护规则运行；另给它们的原生阈值结果作描述性参考。一次重建失败计失败，不能额外调参只救组合方法。
4. 修复成功同时要求：独立参考确认的错误关系数下降；注册视图数 ≥原始的 95%；参考可评点/深度的有效覆盖下降 ≤5 个百分点；GT 几何误差不恶化超过 5%；无新增错误组件合并。没有可评几何 GT 时不能验收完整修复，只能报告物理别名边减少。
5. 指标分母固定为原始输入/参考可见区域，丢掉的相机/表面记入缺失。小样本 8 图中删 1 图已损失 12.5%，会触发失败，不能靠缩小分母通过。报告组件数、最大组件比例、注册图像数、GT 深度覆盖与误差；单纯点数增加/BA residual 降低不等同完整性改善。

不在这轮实现新的全局优化器。P2 若有前后差分，01 才建立 `REPORT.md`；当前没有空结果报告。

## 7. 运行、成本和停止条件

**资源上限（本协议建议）：** P0 人工最多 2 小时、GPU 累积 30 分钟；P1/P2 合计人工最多 6 小时、GPU 累积 2 小时；失败重试计入。首轮数据下载总量 ≤3 GB，权重/环境由 02 独立登记、先查缓存与大小；不为实验新增付费。任一单任务的既有更小预算优先。时间用尽交阻塞/负结果，不顺延。

容量阶梯：双图 smoke →4 图→最多 8 图，batch=1；02 可沿上游 `memory_efficient_inference` / minibatch 设置降低显存。每次 OOM 只允许一次降低视图数的重试，保存失败；改变 N 后所有比较组保持相同 N。每个场景最多原顺序、逆序及 seed=0 固定置乱三种；它们只是敏感性复核，不是独立场景。论文级重复/调参不在本轮范围。

**立即停止该分支：** 数据/权重入口不能在预算内取得；许可无法支持计划使用；没有可信独立标签；图像/参考坐标无法一致；不足场景；强基线无法运行；OOM 或成本上限；组合留出不优于单信号；对照已解决全部目标错误；改善依赖误删/图断裂；必须看留出改阈值才能成立。技术阻塞只否定本轮可执行性；区分 `environment-blocked / reference-insufficient / no-failure-observed / no-increment / harmful-repair / promising-pilot`，不能混写成算法无效。

**02 最低执行清单：**

1. 在自己的 `.workspace/experiments/geometry-audit/` 保存 run manifest：协议 hash、数据列表/hash、来源与许可、模型 SHA/checkpoint hash、Python/Torch/CUDA/GPU、输入顺序/尺度/裁剪、随机种子、所有 flags、时间和内存。
2. P0 用现有上游推理入口跑普通图，保留 camera/depth/learned conf/mask，原始未过滤输出与展示输出分开。获取 TUM 后执行固定选帧与 GT 方向/单位检查；人工确认两个参考相机变换的 round-trip，避免 convention bug。
3. P1 先冻结 `selection.json` 与 `labels.csv`，再计算 `scores.csv`。运行 C/G0/独立几何/DG++/XDG，最后校准固定 CG 与阈值；留出标签可封存在单独文件，在冻结前不给调参流程读取。
4. 记录 3 个关键原生命令/API入口：[MapAnything infer](https://github.com/facebookresearch/map-anything#usage)、[DG++ COLMAP 示例](https://github.com/doppelgangers25/doppelgangers-plusplus#model-usage-in-structure-from-motion)、[XDG 显式 pair 列表](https://github.com/xtcpete/xdg#score-an-explicit-pair-list)。必须使用实际固定 checkout 的帮助/函数签名，不把本文当作已存在的新 runner。
5. XDG 在已准备环境及相应仓库 cwd 下可用的 PowerShell 单行示例（路径由 02 换为已冻结的实际绝对路径）：`python remove_doppelgangers.py --config configs/model_configs/xdg.yaml --ckpt <checkpoint> --pairs_txt <pairs.txt> --input_image_path <images> --output_path <output>`。每行两条相对图像路径；有空格的原文件名先建立确定映射，保留原 hash，不静默截断。
6. 最低结果字段：`run_id, protocol_hash, dataset_version, scene_id, pair_id, split, model_sha, checkpoint_hash, context_N, order, surface_label, pose_label, label_source, label_status, tentative_n, score_C_raw, score_G0_raw, score_G, score_CG, score_DGpp, score_XDG, abstention_reason, rotation_deg, translation_deg, seconds, peak_vram_mb`。可用 CSV/JSON，不创建泛用框架。分数未运行用 null+原因，不能填 0。
7. 交接模型失败、数据失败与真实结果；01 复核解释，03 只消费已批准措辞和可公开素材来源。中央实验/成本登记由主任务单写。

## 8. 当前可公开快照

研究问题：重复结构和视觉相似的不同表面，会怎样影响多视图几何重建；现有置信度与独立估计的几何检查能否互补？

截至 2026-09-22，已完成直接方法比较及 GEO-P0.1 协议，指定普通对照、歧义数据入口、独立标签规则和停止条件。状态为“研究进行中”；按本协议验证的场景数 **0**，本文件没有实验性能、新颖性或修复成功结论。可公开引用本文件的原创文字与一手来源链接；原始图片、模型产物与素材另按来源及真实运行记录审核。
