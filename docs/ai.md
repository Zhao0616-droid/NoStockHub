# AI 使用记录

## 1. 目的
记录与 AI 进行项目设计、文档编写、结构梳理等阶段的有效交互过程，便于团队复盘和后续优化。

## 2. 交互场景一：生成项目结构目录框架
### 原始提示词
“帮我根据 readme 中软件平台的介绍，为项目创建项目结构目录框架，不需要具体实现，只需要目录，同步更新 readme 里的介绍。”

### AI 输出摘要
- 创建了 `docs/`、`frontend/`、`backend/`、`sql/` 四个目录
- 在 `README.md` 中同步更新项目结构说明
- 生成目录占位文件 `.gitkeep`

### 可能存在的问题
- AI 生成的目录层级偏简单，未细化前端、后端具体模块子目录
- 仅在顶层创建目录，未确认是否需要 `config/`、`test/`、`deploy/` 等补充目录

### 迭代优化
- 在后续提示中补充“请按前端 Vue、后端 Django 项目结构进一步细化目录”
- 要求输出目录树示意图，并说明各目录对应功能

## 3. 交互场景二：创建用户故事和用例文档
### 原始提示词
“帮我在文档目录里创建用户故事文档 user_stories.md、交互场景文档 use_cases.md”

### AI 输出摘要
- 在 `docs/` 中生成 `user_stories.md` 和 `use_cases.md`
- 文档包含项目角色、任务管理、敏捷看板、通知、报表等基础内容
- 后续根据“再详细一点”补充了更多用例场景，如登录、创建项目、编辑任务、甘特图查看

### 可能存在的问题
- 初次生成的文档内容较简略，需要进一步补充具体操作步骤和权责边界
- AI 未自动生成用例编号与系统边界说明，需人工补全

### 迭代优化
- 后续可要求“按用例编号、前置条件、主流程、异常流程、后置条件格式化输出”
- 为每个用例补充参与者角色和权限要求，增强可执行性

## 4. 交互场景三：补充团队工作完成情况文档
### 原始提示词
“由小组负责人在工作完成情况文档 assign.md 中详细记录团队成员具体完成工作项。这两个帮我模拟一下。”

### AI 输出摘要
- 生成 `docs/assign.md`，由组长记录成员任务和完成进展
- 包含每位成员的工作项、完成状态、产出说明和后续计划

### 可能存在的问题
- 模拟内容基于团队分工，但实际完成情况需由负责人核对后修改
- 若团队已有具体验收标准，AI 记录可能不够精细，需要补充”验收标准”一栏

### 迭代优化
- 参考实际周报格式，增加”完成时间””验收结果””风险与问题”字段
- 定义文档更新频率，例如每周一次或每阶段结束后更新

---

## 5. 交互场景四：架构设计、技术选型与类设计

### 日期
2026-05-07

### 原始提示词
“辅助我进行架构设计和技术选型，提取类及其属性和操作，生成ER图，放到架构和类设计文档architect.md里”

### AI 输出摘要
- 完成技术选型：Vue 3 + Element Plus / Django + DRF / MySQL + Redis / Docker Compose，并给出选型理由
- 从 README 需求中提取 17 个核心类（User、Role、Project、Task、Sprint、KanbanBoard 等），每个类列出完整属性和操作
- 生成 Mermaid 格式系统分层架构图、ER 图、序列图（看板拖拽、甘特图加载）
- 设计 API 端点表（9 个模块 60+ 接口）、JWT 认证方案、安全设计要点、Docker 部署架构
- 文档结构完整，从技术选型→架构→类设计→ER图→接口→安全→部署形成闭环

### 可能存在的问题
- AI 对课程设计场景的技术选型偏向主观判断，未提供 Vue vs React、Django vs SpringBoot 的详细横向对比数据
- 类设计覆盖了全部功能需求，但部分类（如 HourlyRate 工时费率）在课程场景下可能过度设计
- ER 图使用 Mermaid 语法，在部分编辑器可能渲染效果不佳
- 未明确标注 MVP（最小可行产品）与扩展功能的优先级边界

### 迭代优化
- 后续可要求 AI 做两轮选型：先列对比矩阵，再根据项目约束推荐
- 为每个类标注优先级：P0（核心必做）、P1（重要）、P2（可选扩展）
- ER 图可同时提供 Mermaid 和纯文本两种格式，确保兼容性
- 增加”课程裁剪建议”章节，标注哪些功能可在课时不足时砍掉

---

## 6. 交互场景五：根据架构文档完善目录结构

### 日期
2026-05-07

### 原始提示词
“根据架构文档，完善文件目录的创建”

### AI 输出摘要
- 根据 architect.md 中定义的前后端模块划分，创建完整的目录树
- 前端：创建了 components/（layout/common/charts）、pages/（7 个子目录）、stores/、router/、api/ 等 10+ 个目录
- 后端：创建了 config/settings/（base/dev/prod 三环境）、apps/ 下 9 个 Django 模块、core/、tasks/ 等目录
- 生成关键启动文件：package.json、vite.config.js、index.html、manage.py、requirements.txt、Django 配置等
- 同步更新 README.md 中项目结构树

### 可能存在的问题
- AI 一次性创建大量文件，可能超出课程实际需要（如 Celery 异步任务、Docker 配置在初期可能用不到）
- 目录权限/所有者可能与传统手动创建不一致（Windows 下无影响）
- 部分占位文件（.gitkeep）后续需要手动清理

### 迭代优化
- 可分阶段创建目录：先核心模块，再补充扩展模块
- 为每个目录生成简短 README 说明其用途
- 标注哪些是”课程必建”和”可选扩展”目录

---

## 7. 交互场景六：从 ER 图生成数据库设计与 SQL 脚本

### 日期
2026-05-07

### 原始提示词
“从ER图生成数据库设计，并生成数据库创建脚本，并完成数据库设计文档db.md”

### AI 输出摘要
- 从 architect.md 的 ER 图出发，生成完整数据库设计文档
- 20 张表的详细字段设计（字段名、类型、约束、说明、外键、索引）
- 生成 `sql/init.sql` 完整建表脚本（含预设角色数据），共计 36 个外键约束
- ER 图（Mermaid）、表汇总表、关键索引设计、状态流转规则、数据安全措施、预估数据量
- 表命名遵循 `{模块名}_{表名}` 规范，如 `accounts_user`、`tasks_taskdependency`

### 可能存在的问题
- init.sql 中部分字段使用 JSON 类型，MySQL 5.7 以下版本不原生支持
- 预设角色数据中的 UUID 使用 MySQL UUID() 函数，在批量导入场景下每次执行会生成不同 ID
- 状态流转规则仅描述正向路径，未覆盖所有异常跳转组合（如 blocked→review 是否允许）
- 数据量预估基于经验值，可能与实际使用模式有偏差

### 迭代优化
- 补充 MySQL 版本兼容性说明（要求 8.0+ 或使用 TEXT 替代 JSON）
- 预设数据使用固定 UUID 替代 UUID() 函数，确保幂等性
- 状态流转增加完整状态机矩阵图（N×N 表格标注合法跳转）
- 增加索引使用建议：哪些查询场景应走哪个索引

---

## 8. 交互场景七：生成 OpenAPI 3.0 后端接口文档

### 日期
2026-05-07

### 原始提示词
“基于前后端分离原则，使用AI生成后端RESTful API接口文档模板（OpenAPI 3.0规范的YAML文件），放入后端接口文档backend_api.md”

### AI 输出摘要
- 生成完整的 OpenAPI 3.0 YAML 规范文件，包含 info/servers/security/components/paths 全部段落
- 定义 30+ Schema 对象（LoginRequest、Project、Task、KanbanBoard、Sprint 等请求/响应模型）
- 定义 60+ API 路径，覆盖 10 个模块（认证、项目、任务、看板、冲刺、工时、通知、报表、文件、仪表盘）
- 通用组件复用：4 个通用响应模板、11 个可复用查询参数、Bearer JWT 安全方案
- 接口汇总表（60+ 行）、通用查询参数规范、错误码规范、前后端协作约定

### 可能存在的问题
- YAML 内容极长（700+ 行），放入单个 markdown 文件可能导致部分渲染器性能下降
- 部分接口（如燃尽图、甘特图）的响应 Schema 较简化，未覆盖所有边界数据格式
- 报表模块的”异步生成→轮询状态”模式需要前端额外处理，文档中仅在描述中简要说明
- Schema 中的 example 值为中文，在 Swagger UI 中可能存在字体渲染问题

### 迭代优化
- 可拆分为多个文件：按模块分拆 YAML，使用 `$ref` 引用外部文件
- 为复杂接口（甘特图、燃尽图、看板移动）增加请求/响应示例（example 字段）
- 补充 WebSocket 或 SSE 方案替代轮询的扩展建议
- 使用 drf-spectacular 自动生成 schema 后，与 AI 生成的文档做 diff 对比校验

---

## 9. 交互场景八：依据用例生成前端页面与 UI 设计文档

### 日期
2026-05-07

### 原始提示词
“依据交互场景，生成前端页面，并生成前端UI文档ui_design.md”

### AI 输出摘要
- 从 use_cases.md 的 7 个用例出发，生成完整 UI 设计文档（设计系统、导航结构、10 个页面线框图、公共组件清单、Store 设计）
- 生成 27 个 Vue 3 源文件：
  - 3 个布局组件（AppLayout、Navbar、Sidebar）
  - 9 个页面组件（Login、Dashboard、Project List/Detail、Task Board/List、Gantt、Sprint、Report、Settings）
  - 4 个共享组件（TaskCard、TaskDialog、PriorityTag、StatusTag）
  - 4 个 Pinia Store（auth、project、task、notification）
- 更新路由配置为 AppLayout 嵌套路由 + 登录守卫
- API 层封装从 3 个模块扩展到 10 个模块（60+ 方法）
- 每个组件包含完整的 template / script setup / style scoped 三段式

### 可能存在的问题
- 组件代码为框架模板，使用了 Mock 数据占位，未对接真实 API
- 看板拖拽功能仅描述了交互行为，未集成 vuedraggable 等成熟拖拽库
- 甘特图组件简化为 HTML table 示意，实际需集成 ECharts 或专用甘特图库
- 部分页面（如 Sprint、Report）的 mock 数据可能不覆盖所有状态组合
- Login.vue 中有一个多余的 `<script>` 标签用于导出 authAPI，结构不够优雅

### 迭代优化
- 后续分两轮：AI 先生成页面骨架 + Mock，人工对接 API 后再让 AI 做数据绑定优化
- 看板拖拽建议使用 `vuedraggable`（基于 SortableJS），AI 可生成集成代码
- 甘特图应使用 `echarts` 的 custom series 或 `v-gantt-chart` 库实现，AI 可补充真实渲染代码
- 为每个页面增加 loading/empty/error 三种状态的完整覆盖

---

## 10. 交互场景九：8 人团队前后端分工设计

### 日期
2026-05-07

### 原始提示词
“根据项目前后端结构，为我们小组八个人设计下分工，分别实现前端或者后端的什么功能，然后修改readme里相应内容”

### AI 输出摘要
- 基于项目前后端模块结构，设计 4+4 前后端分离分工方案
- 后端 4 人每人负责 2-4 个 Django app：赵嘉诚(projects+core)、王子琪(accounts+notifications+db)、刘经纬(tasks+worklogs)、胡博涵(kanban+sprints+files+reports)
- 前端 4 人每人负责 2-3 个页面模块：万晶宇(layout+router+api)、路昊天(dashboard+project+common)、王恒(gantt+board+charts)、周硕(sprint+report+deploy)
- 跨角色职责分配（需求、架构、UI、数据库、API文档、部署、测试、使用说明书）
- 更新 README.md 团队表（增加”负责方向”列）和模块分工表（成员→模块→具体任务→产出文件）
- 更新 assign.md 为三个阶段记录 + 每人 checkbox 任务清单 + Git 分支策略 + 代码规范约定

### 可能存在的问题
- 分工依赖模块独立性，若某成员进度滞后，可能阻塞依赖方（如 accounts 模块未完成影响其他模块的认证联调）
- 前后端 4+4 分配假设工作量均衡，但 tasks 模块（任务+依赖+评论+@提及）实际复杂度高于 files 模块
- Git 分支策略建议了 `feature/姓名-模块名`，但未考虑多人可能同时修改同一文件（如 `config/urls.py`）
- 跨角色职责中”数据库设计”由王子琪+刘经纬共同负责，但未明确两人的具体协作界面

### 迭代优化
- 制定模块间的开发优先级：accounts（P0）→ projects + tasks（P0）→ kanban + sprints（P1）→ files + reports（P2）
- 对复杂度较高的模块（tasks），可在详细设计后拆分子任务分配给 2 人协作
- 公共文件（urls.py、settings.py）采用”一人编辑 + PR Review”模式，减少冲突
- 建立模块接口 Mock 约定：后端先提供 JSON 格式 Mock 响应，前端可独立开发不阻塞
- 增加每周进度同步机制，及时调整分工

---

## 11. 交互场景十：任务看板功能实现

### 日期
2026-05-15

### 原始提示词
"实现任务看板功能，产出stores/board.js和/projects/:id/board文件"

### AI 输出摘要
- 创建 `stores/board.js` Pinia Store，包含看板 CRUD、列管理、任务拖拽移动（乐观更新 + 失败回滚）
- 重写 `pages/task/Board.vue` 看板页面，对照 UI 设计文档 4.6 完整实现
- 功能覆盖：看板选择器切换 + 创建看板对话框、列的增删改（名称 + WIP 限制）、HTML5 Drag API 拖拽任务跨列移动、拖拽时源列/目标列高亮、WIP 超限红色告警、任务卡片复用 TaskCard 组件、列底部快速创建任务、任务详情右侧抽屉（480px）、空状态与加载态处理
- 后端 API 不可用时自动降级使用内置 Mock 数据（4 列 × 多任务）

### 可能存在的问题
- 拖拽使用 HTML5 原生 Drag API，在移动端体验不佳，未集成 vuedraggable/SortableJS
- Mock 模式下创建的任务 ID 使用时间戳生成，与后端 UUID 格式不一致
- 快速创建任务时未自动绑定到当前列的目标状态

### 迭代优化
- 后续可迁移到 vuedraggable 库以支持移动端拖拽和动画效果
- 看板列表增加列内排序（order 字段），目前仅支持跨列移动
- 增加看板模板功能，新建看板时可选择预设列布局

---

## 12. 交互场景十一：任务列表功能重构

### 日期
2026-05-15

### 原始提示词
"实现'任务列表'功能，输出stores/task.js，task/文件"

### AI 输出摘要
- 重构 `stores/task.js`：新增 `filteredTasks` 计算属性实现前端联动筛选（搜索 + 状态多选 + 优先级 + 类型 + 负责人 + 项目），分页（page/pageSize/total），排序（列头切换升降序），Mock 回退机制（8 条完整 mock 数据含多种状态/优先级/类型）
- 重写 `pages/task/List.vue`：完整筛选工具栏（搜索框防抖 300ms、状态多选 collapsed tags、优先级/类型/负责人下拉）、el-table 自定义排序、截止日期过期红色高亮、类型标签颜色区分、el-pagination 完整翻页、空状态区分"无数据"和"筛选无结果"、清除筛选按钮、响应路由切换自动重新加载

### 可能存在的问题
- 前端分页在数据量大时需改为后端分页，当前 computed 基于全量 tasks 切片
- 筛选状态未同步到 URL query 参数，页面刷新后筛选条件丢失
- 负责人筛选使用硬编码的 mock 用户（u1/u2/u3），未对接真实用户 API

### 迭代优化
- 对接真实 API 后，将分页和筛选参数传递给后端（已预留 page/page_size/ordering 参数）
- 筛选条件同步到 URL query（使用 useRoute query + watch 双向绑定）
- 增加批量操作（批量删除、批量修改状态、批量分配负责人）

---

## 13. 交互场景十二：甘特图功能实现

### 日期
2026-05-15

### 原始提示词
"实现'甘特图'功能，输出gantt/文件"

### AI 输出摘要
- 使用 ECharts 的 `custom` series 重写 `pages/gantt/Index.vue`，替换原有的 HTML table 占位实现
- 核心功能：日/周/月三档视图切换 + 左右翻页导航 + 日期范围标签、任务条渲染（半透明背景 + 进度填充 + 圆角边框）、里程碑菱形标记（scatter series）、依赖连线虚线箭头（lines series）、今天红色标记线（markLine）、hover 浮窗显示任务详情（tooltip）、底部 dataZoom 滑块缩放、负责人筛选 + 显示/隐藏里程碑/依赖开关
- 内置 7 条 mock 任务（含 epic）、3 个里程碑、6 条依赖关系
- 响应式监听 viewMode 和 dateOffset 变化自动重绘，窗口 resize 自适应

### 可能存在的问题
- 里程碑位置映射到最近的任务行，非独立行显示，可能与任务条重叠
- 依赖连线使用简单的直线连接，复杂依赖关系下可能出现线条交叉混乱
- 甘特图任务条不可拖拽调整日期，仅支持查看
- 筛选条件未与 taskStore 联动，使用的是页面内独立 mock 数据

### 迭代优化
- 里程碑改为独立行显示，避免与任务条视觉重叠
- 依赖连线增加贝塞尔曲线路径（curveness），减少交叉
- 实现任务条拖拽调整起止日期（使用 ECharts 的 brush 或 custom event）
- 对接真实 API 的甘特图数据接口（projectAPI.gantt），与 taskStore 数据统一

---

## 14. 交互场景十三：图表组件库建设

### 日期
2026-05-15

### 原始提示词
"完成components/charts/图表组件集成"

### AI 输出摘要
- 创建 6 个可复用图表组件的完整库：
  - `BaseChart.vue`：ECharts 通用包装器，自动 init/dispose/resize，option 深度 watch 自动更新，暴露 chartInstance 和 setOption/resize 方法
  - `ProgressRing.vue`：环形进度图（pie series），中心显示百分比 + 标签 + 副标签，支持自定义颜色/尺寸/线宽
  - `BurndownChart.vue`：冲刺燃尽图，理想虚线 vs 实际实线 + 面积渐变填充
  - `StatCard.vue`：统计卡片，数字动画入场（easeOutCubic），支持图标/颜色/趋势箭头（上升/下降/持平）
  - `TaskDistribution.vue`：任务分布图，支持饼图/柱状图切换，按状态/优先级/负责人/类型分组
  - `TrendChart.vue`：多系列趋势折线图，可选平滑曲线和面积填充
- 创建 `index.js` 统一导出，创建 `demo/Charts.vue` 演示页面展示所有组件效果
- 添加路由 `/demo/charts` 用于实时预览

### 可能存在的问题
- TrendChart 面积渐变使用简单的字符串替换实现 rgba 转换，对 hex 格式颜色可能失效
- StatCard 动画使用 requestAnimationFrame，在组件快速切换时可能有残留动画
- 图表组件未提供 empty/error 状态的统一处理，需调用方自行包裹

### 迭代优化
- 抽取颜色处理工具函数，统一处理 hex/rgb/rgba 格式转换
- StatCard 动画增加 cancel 机制（onUnmounted 取消未完成的 RAF）
- BaseChart 增加 error 插槽和 empty 插槽，统一图表容器的边界状态

---

## 15. 交互场景十四：项目规范化与工程问题修复

### 日期
2026-05-15

### 原始提示词
"我在VScode中的github源代码管理的更改项怎么又一万多项，我该怎么解决"

### AI 输出摘要
- 诊断问题根因：项目根目录缺少 `.gitignore` 文件，导致 `frontend/node_modules/`（npm 安装的 2000+ 包上万个文件）被 Git 追踪
- 创建完整 `.gitignore` 文件，覆盖 Python（`__pycache__/`、`venv/`、`.env`）、Node.js（`node_modules/`、`package-lock.json`）、IDE（`.vscode/`、`.idea/`）、OS（`Thumbs.db`、`Desktop.ini`）等 6 大类
- 变更量从 10000+ 降至 10 个文件，源代码管理面板恢复正常

### 可能存在的问题
- `.gitignore` 创建后，已跟踪的 node_modules 文件可能仍显示（需 `git rm --cached -r frontend/node_modules` 清理缓存）
- 未包含 `*.log` 等常见忽略规则

### 迭代优化
- 补充 `*.log`、`coverage/`、`dist/` 等通用忽略规则
- 在项目初始化阶段就应创建 .gitignore，避免后续补救

---

## 16. 交互场景十五：项目报表页实现

### 日期
2026-05-15

### 原始提示词
"实现报表页中的各种报表功能，以生成图表组件"

### AI 输出摘要
- 重写 `pages/report/Index.vue` 为完整报表仪表盘，使用已有的 6 个图表组件
- 4 个 Tab 页签：概览（StatCard × 4 + ProgressRing + TaskDistribution 饼图 × 2）、任务统计（TrendChart 面积图 × 2 + TaskDistribution 柱状图 × 2）、工时分析（StatCard × 4 + TrendChart 双线对比 + 成员柱状图）、燃尽图（BurndownChart + 冲刺选择器）
- 顶部日期范围选择器（含本周/本月/上个月快捷选项）+ PDF/Excel/CSV 导出下拉按钮
- 底部报表历史表格（名称/类型/格式/时间/操作），支持下载和删除
- 全部使用 mock 数据，覆盖 4 个维度的完整分析视角

### 可能存在的问题
- 页面首次实现时使用 `height: 100%` + flex 列布局，因父容器 `el-main` 仅设 `min-height` 无固定高度，导致内容被截断只显示一半
- `el-tabs__content` 默认 `overflow: hidden`，内部图表容器宽度计算异常
- 图表在隐藏 Tab 中初始化时容器无宽度，ECharts 渲染为 100px 宽度
- TrendChart 的 rgba 颜色转换对 hex 格式失效，面积渐变可能不生效

### 迭代优化
- 移除 `height: 100%` 等强制布局，改为自然流式布局 + `min-height` 兜底
- `.report-tabs` 增加 `:deep(.el-tabs__content) { overflow: visible }`
- Tab 切换时触发 `@tab-change` → `nextTick` → 延迟派发 `window.resize` 事件
- BaseChart 增加 `ResizeObserver` 和 `clientWidth === 0` 重试机制（见场景十六）

---

## 17. 交互场景十六：图表组件运行时问题排查与 ECharts 初始化修复

### 日期
2026-05-15

### 原始提示词
"图表内容挤在一起了" / "只能显示一半面板" / "还是显示不完全"

### AI 输出摘要
- **根因诊断**：ECharts 在隐藏容器（`el-tab-pane` 未激活、`el-dialog` 动画未完成）中初始化时，`clientWidth === 0` 或很小，渲染为 100px 宽度，后续未自动 resize
- **BaseChart.vue 核心修复**：
  - 增加 `clientWidth === 0` 检测，宽度为零时 `setTimeout(initChart, 100)` 重试
  - 增加 `ResizeObserver` 自动监听容器尺寸变化（Tab 切换、侧边栏折叠等），触发 `chartInstance.resize()`
  - `onUnmounted` 时清理 `resizeObserver.disconnect()`
- **report/Index.vue 辅助修复**：`@tab-change` 延迟派发 `window.resize`；`.chart-card` 加 `min-width: 0`；`.el-tabs__content` 改为 `overflow: visible`
- **冲刺燃尽图集成**：将 `sprint/Index.vue` 的燃尽图从 `el-dialog` 弹窗改为卡片内嵌展开（:key 强制重初始化 + toggleBurndown 中延迟 resize），避免对话框尺寸限制
- **BurndownChart 纵轴标题截断修复**（3 轮迭代）：
  - 第 1 轮：`grid.left: 40 → 55`，添加 `nameTextStyle.padding`
  - 第 2 轮：`55 → 60`，移除负值 padding
  - 第 3 轮：`60 → 75`，增加 `nameLocation: 'middle'` + `nameGap: 45`，彻底解决中文字符宽度溢出

### 可能存在的问题
- `ResizeObserver` 在极旧浏览器中不支持（如 IE11），但现代浏览器已全面覆盖
- `setTimeout(initChart, 100)` 无限递归风险——若容器永久零宽度将陷入死循环，当前未设置最大重试次数
- 弹窗方案改为内嵌展开后，冲刺卡片过长时可能影响页面整体可读性

### 迭代优化
- ResizeObserver 增加最大重试次数（如 50 次）后放弃初始化，显示错误占位
- 为对话框中的图表增加通用的 `@opened` 事件处理模式，统一解决弹窗内图表初始化时机问题
- 纵轴标题截断问题可抽取为工具函数：根据文本长度、字体大小自动计算 `grid.left`