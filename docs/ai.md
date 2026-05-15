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

## 11. 交互场景十：accounts 认证模块开发与环境调试

### 日期
2026-05-08

### 原始提示词
"前置工作已完成，请告知我的开发任务及步骤，并协助完成 accounts 模块的代码实现与接口验证。"

### AI 输出摘要
- 阅读项目结构与前置代码（core/models.py、sql/init.sql、config/settings/base.py），梳理刘经纬的 6 项任务并按依赖顺序排列：models → settings → serializers → views → urls → admin
- 生成 accounts 模块完整代码：User(AbstractUser, TimestampedModel) 自定义用户模型（含 Role 模型）、RegisterSerializer / LoginSerializer / UserSerializer 三个序列化器、RegisterView / LoginView / UserProfileView 三个视图、JWT 认证路由（register / login / token/refresh / profile）
- 修改 config/settings/base.py 取消 AUTH_USER_MODEL = 'accounts.User' 注释，启用自定义用户模型
- 修复 Docker 环境两个问题：(1) Dockerfile apt-get 网络失败 → 添加阿里云 Debian 镜像源；(2) 后端启动时 MySQL 未就绪 → docker-compose.yml 为 db 服务添加 healthcheck（mysqladmin ping），backend 的 depends_on 升级为 condition: service_healthy
- 定位接口测试失败根因：sql/init.sql 手动建表缺少 Django AbstractUser 默认字段（is_superuser/is_staff/date_joined），通过 DROP DATABASE + Django migrate 重建匹配表结构
- 确认后端认证路由前缀为 /api/auth/（非 /api/accounts/），提供 PowerShell 环境下的 Invoke-RestMethod 测试命令和 Git 合并冲突处理流程（merge --abort → pull --no-edit → push）

### 可能存在的问题
- sql/init.sql 中手动建表与 Django AbstractUser 模型字段不兼容，当前通过 DROP DATABASE + migrate 临时解决，后续其他模块的表（如 projects、tasks 等）也可能遇到类似字段缺失问题
- docker-compose.yml 中 db 服务挂载了 ./sql/init.sql 到 /docker-entrypoint-initdb.d/，每次重建数据库容器都会重新执行建表脚本，可能覆盖或冲突 migrate 生成的表结构
- Django settings 中 base.py 的 DEBUG = False + ALLOWED_HOSTS = []，Docker 开发环境下不便于调试；建议开发时使用 dev.py（DEBUG=True, ALLOWED_HOSTS=['*']）
- 前端 Login.vue 中 authAPI.register 调用的 API 路径需与后端实际路径 /api/auth/register/ 对齐，前后端联调时需验证
- notifications 模块尚未开发，但前端 layout 组件可能已引用通知 store（stores/notification.js），需关注联调依赖

### 迭代优化
- 移除 sql/init.sql 中 accounts_role 和 accounts_user 建表语句，交给 Django migrations 管理，避免手动 SQL 与 ORM 模型冲突
- 建议刘经纬后续任务按优先级排：accounts/admin.py（Django Admin 配置）→ notifications/models.py（通知模型）→ notifications 完整链路（serializers + views + urls）
- accounts 模块后续迭代应增加：密码重置、邮箱验证、角色权限 CRUD 接口、登录失败锁定与双因素认证
- 项目应补充 .env.example 文件，明确 DB_PASSWORD 等环境变量的默认值，降低新成员环境搭建成本
- 建议团队统一使用 docker-compose down -v 清理卷后重建标准流程，减少手动操作数据库带来的环境不一致
