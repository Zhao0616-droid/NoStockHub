# 工作完成情况记录

## 记录说明
由项目组负责人赵嘉诚负责汇总团队成员在当前阶段的实际完成工作与后续计划，方便项目管理、任务跟踪与验收。

---

## 阶段一：需求分析与项目结构搭建（已完成）

### 阶段成果
- `README.md` 需求分析（功能需求 9 大模块 + 非功能需求 5 类 + 约束条件）
- `docs/user_stories.md` 用户故事（5 类角色共 15 条）
- `docs/use_cases.md` 用例交互场景（7 个用例，含前置/主流程/异常/后置条件）
- `docs/ai.md` AI 使用记录（3 次交互场景）
- 项目顶层目录框架搭建（frontend/ backend/ sql/ docs/）

### 成员工作项

| 成员 | 负责方向 | 具体工作 |
|------|---------|---------|
| 王子琪 | 需求分析 + 前端架构 | 功能需求/非功能需求/约束条件撰写、用户故事与用例文档主笔、前端架构初步调研、README 项目结构维护、团队信息更新 |
| 赵嘉诚 | 系统设计 + 整体协调 | 整体任务协调、文档框架规划与验收、系统设计主笔、数据库整体方案、Docker 部署方案设计 |


## 阶段二：系统设计（已完成）

### 阶段成果
- `docs/architect.md` 架构与类设计（技术选型、分层架构图、17 个核心类、ER 图、API 端点表、序列图、安全设计、部署架构）
- `docs/db.md` 数据库设计（ER 图、21 张表设计、索引设计、状态流转规则、预估数据量）
- `docs/backend_api.md` 后端 API 文档（OpenAPI 3.0 YAML、30+ Schema、60+ 接口、前后端协作约定）
- `docs/ui_design.md` 前端 UI 设计文档（设计系统、10 个页面线框图、14 个公共组件、7 个 Store）
- `sql/init.sql` 数据库初始化脚本（21 张表 + 预设角色数据）
- 前端页面组件框架代码（10 个页面 + 3 个布局组件 + 4 个共享组件 + 4 个 Store）
- `docker-compose.yml` + `Dockerfile`（MySQL/Redis/Django/Celery/Vue 五服务编排）

### 成员工作项

| 成员 | 负责方向 | 具体工作 |
|------|---------|---------|
| 赵嘉诚 | 架构设计 + 整体协调 | 整体架构设计参与、architect.md（技术选型/分层架构图/17核心类/ER图/API端点表）、db.md（21张表设计/索引/状态流转）、backend_api.md（OpenAPI 3.0 YAML/60+接口）、ui_design.md（10页面线框图/14公共组件）主笔 |
| 王子琪 | 需求分析 + 文档 | 需求文档对接、用例补充、团队分工文档更新 |
| 万晶宇 | 前端核心 | 前端页面框架搭建（10页面+3布局+4共享组件+4 Store）、API层10模块封装、路由配置 |
| 王恒 | 后端核心 | 后端项目结构初始化、projects 模块设计参与 |
| 周硕 | 数据库 | 数据库设计参与、sql/init.sql 建表脚本编写 |
| 刘经纬 | 认证模块 | accounts 模块设计参与、Django Admin 配置方案 |

---

## 阶段三：编码实现（进展中，部分已完成）

### 后端团队任务清单

#### 王恒 — 后端架构 + projects + core
- [x] `config/settings/` 三环境配置完善（base/dev/prod）
- [x] `core/models.py` BaseModel / TimestampedModel
- [x] `core/permissions.py` 项目成员权限、管理者权限
- [ ] `core/pagination.py` 标准分页 + 异常处理
- [x] `apps/projects/models.py` Project / ProjectMember / ProjectTemplate / Milestone（120行）
- [x] `apps/projects/serializers.py` 序列化器（含嵌套/校验，177行）
- [x] `apps/projects/views.py` ViewSet（CRUD + 成员管理 + 甘特图数据，187行）
- [x] `apps/projects/urls.py` 路由注册
- [x] `apps/projects/migrations/0001_initial.py` 初始化迁移（105行）
- [ ] 后端代码 Review（全员）

> 产出：初始化后端项目结构（config/settings/base|dev|prod 三环境 + core/models|permissions），完成 projects 模块全栈（模型/序列化器/视图/路由/迁移），共 30 files, 516+ 行新增。

#### 刘经纬 — accounts + notifications + 数据库
- [x] `apps/accounts/models.py` User / Role（继承 BaseModel / AbstractUser，UUID 主键）
- [x] `apps/accounts/serializers.py` 注册/登录/资料序列化器
- [x] `apps/accounts/views.py` JWT 登录/注册/Token 刷新/资料修改/改密
- [x] `apps/accounts/urls.py` 认证路由
- [x] `apps/accounts/migrations/0001_initial.py` 初始化迁移
- [x] `apps/accounts/migrations/0002_align_init_sql_user_schema.py` init.sql 用户表与 Django 对齐
- [x] `config/settings/base.py` 启用 AUTH_USER_MODEL
- [x] `apps/notifications/models.py` Notification
- [x] `apps/notifications/views.py` 通知列表/标记已读/全部已读
- [x] `apps/notifications/services.py` / `utils.py` 创建通知封装（tasks 模块调用）
- [x] `sql/init.sql` 按模型变更同步更新
- [x] Django Admin 后台配置（accounts / notifications 等）

> 产出：完成用户认证模块全栈开发（9 files, 235+ 行），含 JWT 登录/注册/Token 刷新/用户信息接口。

#### 周硕 — tasks + worklogs
- [x] `apps/tasks/models.py` Task / TaskDependency / Comment / Mention（110行）
- [x] `apps/tasks/serializers.py` 任务序列化器（含嵌套子任务/依赖/评论，66行）
- [x] `apps/tasks/views.py` 任务CRUD / 状态流转 / 依赖管理 / 评论（143行）
- [x] `apps/tasks/urls.py` 任务路由
- [x] `apps/worklogs/models.py` WorkLog / HourlyRate（43行）
- [x] `apps/worklogs/serializers.py` 工时序列化器（18行）
- [x] `apps/worklogs/views.py` 工时CRUD / 汇总统计（52行）
- [x] `apps/worklogs/urls.py` 工时路由
- [ ] 数据库迁移管理（makemigrations + migrate）

> 产出：完成任务和工时记录模块全栈开发（8 files, 459+ 行），Task 支持子任务嵌套/依赖关系/评论/@提及，WorkLog 支持工时登记与汇总。

#### 赵嘉诚 — kanban + sprints + files + reports + 整体协调 + 联调修复
- [x] `apps/kanban/models.py` KanbanBoard / KanbanColumn / TaskColumn（77行）
- [x] `apps/kanban/serializers.py` 看板序列化器（98行）
- [x] `apps/kanban/views.py` 看板CRUD / 列管理 / 移动任务（121行）
- [x] `apps/kanban/urls.py` 看板路由
- [x] `apps/sprints/models.py` Sprint（37行）
- [x] `apps/sprints/serializers.py` 冲刺序列化器（125行）
- [x] `apps/sprints/views.py` 冲刺CRUD / 启动 / 完成 / 燃尽图数据（182行）
- [x] `apps/sprints/urls.py` 冲刺路由
- [x] `apps/files/models.py` Attachment（37行）
- [x] `apps/files/serializers.py` 文件序列化器（32行）
- [x] `apps/files/views.py` 文件上传(安全校验50MB/MIME白名单) / 下载 / 删除（156行）
- [x] `apps/files/urls.py` 文件路由
- [x] `apps/reports/models.py` Report（39行）
- [x] `apps/reports/serializers.py` 报表序列化器（49行）
- [x] `apps/reports/views.py` 报表异步生成 / 下载（67行）
- [x] `apps/reports/tasks.py` Celery 异步任务（138行）
- [x] `apps/reports/urls.py` 报表路由
- [x] 4 个模块初始化迁移文件（kanban/sprints/files/reports）
- [x] `docker-compose.yml` 五服务编排 + Dockerfile
- [x] 注册登录联调修复（UUID 主键适配、Token 嵌套格式提取、Django 配置切换）
- [x] 仪表盘后端 API（`GET /api/dashboard/`）对接真实数据，去除硬编码
- [x] 模型/迁移一致性修复（tasks description null、order 字段、accounts/worklogs 迁移对齐）
- [x] 系统架构设计、数据库设计、ER 图、API 文档

> 产出：完成 4 个后端模块全栈开发（25 files, 1551+ 行），含看板/冲刺/文件安全上传/报表 Celery 异步生成。主导整体架构设计、Docker 部署、注册登录联调修复、仪表盘真实数据对接、模型迁移对齐等跨模块工作。

---

### 前端团队任务清单

#### 王子琪 — 需求分析 + 前端架构 + 文档
- [x] README.md 项目说明、需求分析（功能需求 9 大模块 + 非功能需求）
- [x] `docs/user_stories.md` 用户故事（5 类角色共 15 条）
- [x] `docs/use_cases.md` 用例交互场景（7 个用例）
- [x] `docs/ai.md` AI 使用记录（初版框架）
- [x] `docs/assign.md` 团队分工记录
- [x] 项目顶层目录框架搭建（frontend/ backend/ sql/ docs/）

> 产出：负责需求分析阶段全部文档主笔，项目顶层结构规划，README 团队信息与模块分工维护。

#### 路昊天 — Dashboard + Project 页面 + 公共组件
- [x] `pages/dashboard/Index.vue` 仪表盘（统计卡片/我的任务/项目/活动流）
- [x] `pages/project/List.vue` 项目列表（卡片网格/搜索/状态筛选/创建弹窗）
- [x] `pages/project/Detail.vue` 项目详情（进度环/概览/成员/里程碑/活动）
- [x] `components/common/TaskCard.vue` 可拖拽任务卡片
- [x] `components/common/TaskDialog.vue` 任务创建/编辑表单
- [x] `components/common/PriorityTag.vue` 优先级标签
- [x] `components/common/StatusTag.vue` 状态标签
- [x] `stores/project.js` 项目状态 Store
- [x] README.md 团队信息维护

> 产出：完成 Dashboard 仪表盘页面、Project 列表/详情页面、4 个公共组件、项目 Store，覆盖页面骨架与 mock 数据交互。

#### 万晶宇 — 甘特图 + 看板 + 任务列表 + 图表组件 + 报表/冲刺页
- [x] `pages/gantt/Index.vue` 甘特图（ECharts 时间线/日周月视图切换/依赖连线，533行重写）
- [x] `pages/task/Board.vue` 看板（列拖拽/任务卡片/抽屉详情/WIP限制，598行重写）
- [x] `pages/task/List.vue` 任务列表（表格/多选筛选/排序/批量操作，366行重写）
- [x] `pages/report/Index.vue` 报表仪表盘（概览/任务统计/工时分析/燃尽图，498行重写）
- [x] `pages/sprint/Index.vue` 冲刺管理（活跃冲刺/燃尽图集成，27行增量）
- [x] `components/charts/BaseChart.vue` ECharts 通用包装器（ResizeObserver + 零宽度重试）
- [x] `components/charts/BurndownChart.vue` 冲刺燃尽图（理想虚线 vs 实际实线）
- [x] `components/charts/ProgressRing.vue` 环形进度图
- [x] `components/charts/StatCard.vue` 统计卡片（数字动画入场）
- [x] `components/charts/TaskDistribution.vue` 任务分布图（饼图/柱状图切换）
- [x] `components/charts/TrendChart.vue` 多系列趋势折线图
- [x] `components/charts/index.js` 图表组件统一导出
- [x] `pages/demo/Charts.vue` 图表组件演示页（241行）
- [x] `stores/task.js` 任务状态 Store（筛选/分页/排序/mock回退，204行）
- [x] `stores/board.js` 看板状态 Store（列CRUD/拖拽/乐观更新，200行）
- [x] `docs/ai.md` AI 使用记录补充（交互场景十~十六）

> 产出：前端开发量最大的成员。完成 6 个图表组件库、甘特图/看板/任务列表三大核心页面重写、报表仪表盘和冲刺管理页实现、2 个 Store，共 19 files, 2582+ 行新增（第二次提交：5 files, 673+ 行）。解决了 ECharts 隐藏容器初始化零宽度、弹窗内容截断、燃尽图纵轴中文溢出等运行时问题。

#### 胡博涵 — Sprint + Report 前端 + 部署
- [x] README.md 团队信息维护
- [ ] `pages/sprint/Index.vue` 冲刺管理（已由万晶宇完成燃尽图集成）
- [ ] `pages/report/Index.vue` 报表（已由万晶宇完成报表仪表盘）
- [ ] `stores/sprint.js` 冲刺状态 Store
- [ ] `stores/notification.js` 通知状态 Store
- [ ] `docker-compose.yml` 部署编排（已由赵嘉诚完成）
- [ ] Nginx 反向代理配置
- [ ] 前端测试用例（组件渲染/API Mock/用户交互）

> 备注：原分配的前端 Sprint/Report 页面由万晶宇协作完成，胡博涵主要负责部署与测试相关工作。待补充 Docker/Nginx/测试产出。

---

### 近期联调修复与功能补充（2026-05-22）

以下为赵嘉诚在阶段三后期完成的跨模块联调修复、缺失功能补充与测试工作：

| 类别 | 具体工作 | 涉及文件 |
|------|---------|---------|
| **Postman 接口测试** | 生成 10 模块 55 请求 76 断言完整测试集合，Newman CLI 全量通过（0 失败，15.7s） | `docs/postman_collection.json`、`docs/test.md` |
| **删除功能补全** | 全项目 10 模块删除能力审计，修复 7 处缺失：Report 后端 destroy + 磁盘清理、前端 reportAPI.delete、项目/冲刺/看板删除按钮、工作日志/文件/费率 3 个管理页面新建 + 路由 + 侧边栏 | `backend/apps/reports/views.py`、`frontend/src/api/index.js`、`frontend/src/pages/report/Index.vue`、`frontend/src/pages/project/Detail.vue`、`frontend/src/pages/sprint/Index.vue`、`frontend/src/pages/task/Board.vue`、`frontend/src/pages/worklog/Index.vue`（新建）、`frontend/src/pages/files/Index.vue`（新建）、`frontend/src/pages/rates/Index.vue`（新建）、`frontend/src/router/index.js`、`frontend/src/components/layout/Sidebar.vue` |
| **Bug 修复** | ① 任务负责人硬编码"张三/李四"改为加载项目真实成员 ② 任务列表不显示：`filteredTasks` 只检查 `project_id` 但 API 返回 `project`，修复双字段兼容 ③ 任务创建/更新/删除在 API 失败时静默写 mock 假数据，改为直接抛错 ④ 费率 API 路由被 WorkLogViewSet 详情正则拦截，改为显式 URL + `<uuid:pk>` ⑤ 看板拖拽字段 `to_column_id` → `target_column_id` 对齐后端 ⑥ 报表 Celery 调用未 try-except，Redis 不可用时 500，改为捕获异常返回 202 | `frontend/src/components/common/TaskDialog.vue`、`frontend/src/stores/task.js`、`backend/apps/worklogs/urls.py`、`frontend/src/stores/board.js`、`backend/apps/reports/views.py` |
| **看板功能增强** | ① 新建看板自动创建 4 个默认列（待办/进行中/审核中/已完成）② 加载列时自动同步项目任务到第一列（未分配任务归入"待办"）③ 从看板列创建任务后自动入列 | `backend/apps/kanban/views.py`、`frontend/src/pages/task/Board.vue` |
| **费率管理增强** | 添加用户选择器（默认当前用户可选项目成员）、后端 `HourlyRateViewSet.perform_create` 自动设置用户 | `frontend/src/pages/rates/Index.vue`、`backend/apps/worklogs/views.py`、`backend/apps/worklogs/serializers.py` |
| **工时管理增强** | 任务从手动输入 UUID 改为下拉选择项目任务、校验错误提示从"记录失败"改为字段级中文提示 | `frontend/src/pages/worklog/Index.vue` |
| **错误提示优化** | 多处 `catch` 只取 `detail` 导致字段级校验错误无提示，统一添加 `formatErrors` 遍历所有字段拼接 | `frontend/src/pages/project/Detail.vue`、`frontend/src/pages/rates/Index.vue`、`frontend/src/pages/worklog/Index.vue` |

> 产出：2 个后端文件修改 + 3 个前端新建页面 + 9 个前端文件修改 + 8 处 Bug 修复 + 1 个 Postman 测试集合。看板与任务列表数据同步打通，删除功能全模块覆盖，接口测试 76 断言全绿。

### 集中测试与 Debug（2026-05-29）

以下为赵嘉诚在阶段四进行的集中测试、Bug 排查与修复工作：

| 序号 | 问题 | 根因 | 修复方案 | 涉及文件 |
|------|------|------|---------|---------|
| 1 | 报表页面空白 | `filteredTasks` computed 递归自引用（`filteredTasks.value.filter(...)`）导致无限循环 | 改为 `allTasks.value.filter(...)` | `frontend/src/pages/report/Index.vue` |
| 2 | 冲刺只显示一个 | 后端启动新冲刺未停用旧活跃冲刺；前端排除所有 active 冲刺 | 后端 `start()` 更新其他冲刺为 COMPLETED；前端 `plannedSprints` 仅排除首个 active 冲刺 | `backend/apps/sprints/views.py`、`frontend/src/pages/sprint/Index.vue` |
| 3 | 看板与任务列表状态不同步 | 动态 `import()` Vite 路径解析失败；两个 Store 未互相同步 | 改为静态 `import { useTaskStore }` / `import { useBoardStore }`，在 async action 中跨 Store 更新 | `frontend/src/stores/board.js`、`frontend/src/stores/task.js` |
| 4 | 项目进度始终为 0% | `Task.progress` 整数字段默认 0，`Avg('progress')` 始终返回 0 | 改为按任务状态计算 `done/total × 100` | `backend/apps/projects/serializers.py`、`backend/apps/projects/views.py` |
| 5 | 里程碑无法增删改 | 后端仅支持 GET/POST；前端无编辑/删除入口 | 后端 `milestones` action 新增 PATCH/DELETE；前端完整 CRUD UI | `backend/apps/projects/views.py`、`frontend/src/pages/project/Detail.vue`、`frontend/src/api/index.js` |
| 6 | 甘特图周/日视图无显示 | xAxis 未设置时间粒度，标签格式不区分视图模式 | 增加 `minInterval`/`maxInterval` 控制 + `axisLabel.formatter` 按 `day`/`week`/`month` 输出不同格式 | `frontend/src/pages/gantt/Index.vue` |
| 7 | 头像上传失败 | data URL 存入 `URLField(max_length=200)` 被拒 | 改为真实文件上传（FormData + fileAPI.upload）；`max_length` 扩至 500 + 新增迁移 | `frontend/src/pages/settings/Index.vue`、`backend/apps/accounts/models.py`、`backend/apps/accounts/migrations/0003_alter_user_avatar.py` |
| 8 | 字体调整未生效 | 值仅存 localStorage 未应用到 DOM | `watch(fontSize)` + `applyFontSize()` 设置 `document.documentElement.style.fontSize` | `frontend/src/pages/settings/Index.vue` |
| 9 | 语言设置未持久化 | localStorage 恢复逻辑不完整 | 修正 `onMounted` 中从 localStorage 恢复设置并实时应用 | `frontend/src/pages/settings/Index.vue` |
| 10 | 非管理员看板空白 | `manage_columns` GET 要求 `IsProjectManager`，普通成员 403 | GET 改为 `IsProjectMember`，POST 保持 `IsProjectManager` | `backend/apps/kanban/views.py` |
| 11 | 个人资料修改失败 | PUT 缺少 read_only_fields → username 校验失败 | 增加 `read_only_fields` + 前端 PUT → PATCH | `backend/apps/accounts/serializers.py`、`frontend/src/api/index.js` |
| 12 | 文件上传不持久 | Nginx `/media/` 使用 proxy_pass，容器重建后丢失 | 改为 `alias` 直接文件系统服务 + docker-compose 挂载 `media_data` volume | `frontend/nginx/default.conf`、`docker-compose.prod.yml` |
| 13 | 登录不支持邮箱 | 仅 `ModelBackend` 支持用户名登录 | 新增 `EmailOrUsernameBackend`（`Q(username\|email)` 查询）+ settings 配置 + 前端 UI 更新 | `backend/apps/accounts/backends.py`（新建）、`backend/config/settings/base.py`、`frontend/src/pages/settings/Login.vue` |

> 产出：排查并修复 13 个 Bug，覆盖报表/冲刺/看板/任务/进度/甘特图/头像/字体/语言/权限/资料/文件/登录全模块。涉及 17 个文件、7 个后端文件、10 个前端文件。

### 团队成员测试参与

在阶段四集中测试阶段，各成员在各自负责模块范围内进行了功能测试和联调测试，发现并报告了多个 Bug（报表空白、冲刺显示、状态同步、进度 0%、甘特图视图、头像上传、字体调整、权限拦截、文件持久化、登录方式等），由赵嘉诚统一汇总、定位根因并修复。

### 云端部署

赵嘉诚负责的生产环境部署工作：

| 类别 | 具体工作 | 涉及文件 |
|------|---------|---------|
| **Docker Compose 生产编排** | 五服务编排（db/redis/backend/celery/frontend）、环境变量注入（DB/Redis/JWT/CORS）、网络隔离、依赖启动顺序（depends_on + healthcheck） | `docker-compose.prod.yml` |
| **Nginx 反向代理** | `/api/` → backend:8000 代理转发、`/media/` → `/app/media/` 直接文件系统服务 + 7 天缓存、SPA 路由 fallback（`try_files $uri /index.html`） | `frontend/nginx/default.conf` |
| **Dockerfile 多阶段构建** | 前端：node构建阶段 + nginx运行阶段；后端：Python依赖安装 + gunicorn 启动 | `backend/Dockerfile`、`frontend/Dockerfile` |
| **媒体文件持久化** | `media_data` named volume 挂载到 frontend 容器（`:ro`）供 Nginx 读取，vite dev server 添加 `/media` proxy | `docker-compose.prod.yml`、`frontend/vite.config.js` |
| **静态资源服务** | `STATIC_URL`/`MEDIA_URL`/`MEDIA_ROOT` 配置 + DEBUG 模式下 `static()` 辅助开发 | `backend/config/settings/base.py`、`backend/config/urls.py` |
| **服务器部署** | 代码推送 + 服务器 docker-compose 重建流程指导 | 部署命令文档 |

> 产出：完成生产环境 Docker Compose 全栈编排、Nginx 反向代理与文件服务、媒体文件持久化方案、多阶段构建优化。

---


## 开发约定

### Git 分支策略
- `master` — 主分支，仅合并经过 Review 的代码
- `feature/姓名-模块名` — 个人开发分支，如 `feature/wangheng-projects`
- 每完成一个模块提交 PR，由组长 Review 后合并

### 代码规范
- 前端：ESLint + Prettier，提交前 `npm run lint`
- 后端：PEP 8，DRF ViewSet 命名 `{Model}ViewSet`
- Commit Message：`feat: 添加任务状态流转` / `fix: 修复看板拖拽异常` / `docs: 更新API文档`

### 接口联调
- 前端通过 `vite.config.js` proxy 代理到本地 Django `:8000`
- 后端先提供 Mock 数据 / Swagger UI 可交互调试
- 每个模块完成后前后端联调确认

---

## 实验报告总结（赵嘉诚）

本次课程设计完成了软件项目管理平台 NoStockHub 的全栈开发，采用 Vue 3 + Element Plus 前端、Django REST Framework 后端、MySQL + Redis 数据层、Docker Compose 容器化部署的技术架构。平台覆盖项目管理、任务看板、甘特图、冲刺管理、工时记录、文件管理、报表生成、通知系统等 9 大功能模块。

