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
| 王子琪 | 需求分析 + 前端架构 | 功能需求/非功能需求/约束条件撰写、用户故事与用例文档主笔、前端架构初步调研 |
| 赵嘉诚 | 系统设计 + 整体协调 | 整体任务协调、文档框架规划与验收、系统设计主笔、数据库整体方案 |


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
| 赵嘉诚 | files + reports | 整体架构设计参与、architect.md、db.md、backend_api.md、ui_design设计 |

---

## 阶段三：编码实现（进行中）

### 后端团队任务清单

#### 王恒 — 后端架构 + projects + core
- [ ] `config/settings/` 三环境配置完善（base/dev/prod）
- [ ] `core/models.py` BaseModel / TimestampedModel
- [ ] `core/permissions.py` 项目成员权限、管理者权限
- [ ] `core/pagination.py` 标准分页 + 异常处理
- [ ] `apps/projects/models.py` Project / ProjectMember / ProjectTemplate / Milestone
- [ ] `apps/projects/serializers.py` 序列化器（含嵌套/校验）
- [ ] `apps/projects/views.py` ViewSet（CRUD + 成员管理 + 甘特图数据）
- [ ] `apps/projects/urls.py` 路由注册
- [ ] 后端代码 Review（全员）

#### 刘经纬 — accounts + notifications + 数据库
- [ ] `apps/accounts/models.py` User / Role（继承 BaseModel）
- [ ] `apps/accounts/serializers.py` 注册/登录/资料序列化器
- [ ] `apps/accounts/views.py` JWT 登录/注册/Token刷新/资料修改/改密
- [ ] `apps/accounts/urls.py` 认证路由
- [ ] `apps/notifications/models.py` Notification
- [ ] `apps/notifications/views.py` 通知列表/标记已读/全部已读
- [ ] `sql/init.sql` 按模型变更同步更新
- [ ] Django Admin 后台配置

#### 周硕 — tasks + worklogs
- [ ] `apps/tasks/models.py` Task / TaskDependency / Comment / Mention
- [ ] `apps/tasks/serializers.py` 任务序列化器（含嵌套子任务/依赖/评论）
- [ ] `apps/tasks/views.py` 任务CRUD / 状态流转 / 依赖管理 / 评论
- [ ] `apps/tasks/urls.py` 任务路由
- [ ] `apps/worklogs/models.py` WorkLog / HourlyRate
- [ ] `apps/worklogs/views.py` 工时CRUD / 汇总统计
- [ ] `apps/worklogs/urls.py` 工时路由
- [ ] 数据库迁移管理（makemigrations + migrate）

#### 赵嘉诚 — kanban + sprints + files + reports
- [ ] `apps/kanban/models.py` KanbanBoard / KanbanColumn / TaskColumn
- [ ] `apps/kanban/views.py` 看板CRUD / 列管理 / 移动任务
- [ ] `apps/sprints/models.py` Sprint
- [ ] `apps/sprints/views.py` 冲刺CRUD / 启动 / 完成 / 燃尽图数据
- [ ] `apps/files/views.py` 文件上传(安全校验) / 下载 / 删除
- [ ] `apps/reports/views.py` 报表异步生成 / 下载
- [ ] `tasks/celery.py` Celery 异步任务配置

---

### 前端团队任务清单

#### 王子琪 — 前端架构 + Layout + 认证与路由
- [ ] `components/layout/AppLayout.vue` 整体布局（侧边栏+顶栏+内容区）
- [ ] `components/layout/Navbar.vue` 顶栏（面包屑/通知/用户菜单）
- [ ] `components/layout/Sidebar.vue` 侧边栏（菜单/项目子导航自动切换）
- [ ] `router/index.js` 路由配置 + 导航守卫（Token校验）
- [ ] `api/request.js` Axios 拦截器（JWT自动附带+过期刷新）
- [ ] `api/index.js` 10 个模块 API 方法封装
- [ ] `pages/settings/Login.vue` 登录/注册表单
- [ ] `pages/settings/Index.vue` 系统设置页
- [ ] `stores/auth.js` 认证状态 Store

#### 路昊天 — Dashboard + Project 页面 + 公共组件
- [ ] `pages/dashboard/Index.vue` 仪表盘（统计卡片/我的任务/项目/活动流）
- [ ] `pages/project/List.vue` 项目列表（卡片网格/搜索/状态筛选/创建弹窗）
- [ ] `pages/project/Detail.vue` 项目详情（进度环/概览/成员/里程碑/活动）
- [ ] `components/common/TaskCard.vue` 可拖拽任务卡片
- [ ] `components/common/TaskDialog.vue` 任务创建/编辑表单
- [ ] `components/common/PriorityTag.vue` 优先级标签
- [ ] `components/common/StatusTag.vue` 状态标签
- [ ] `stores/project.js` 项目状态 Store

#### 万晶宇 — 甘特图 + 看板 + 任务列表 + 图表组件
- [ ] `pages/gantt/Index.vue` 甘特图（ECharts 时间线/日周月视图切换/依赖连线）
- [ ] `pages/task/Board.vue` 看板（列拖拽/任务卡片/抽屉详情/WIP限制）
- [ ] `pages/task/List.vue` 任务列表（表格/多选筛选/排序/批量操作）
- [ ] `components/charts/` 图表组件（甘特图/燃尽图/进度环/统计图）
- [ ] `stores/task.js` 任务状态 Store
- [ ] `stores/board.js` 看板状态 Store

#### 胡博涵 — Sprint + Report 页面 + 部署与测试
- [ ] `pages/sprint/Index.vue` 冲刺管理（活跃冲刺/燃尽图弹窗/启动完成）
- [ ] `pages/report/Index.vue` 报表（生成表单/异步状态/历史下载）
- [ ] `stores/sprint.js` 冲刺状态 Store
- [ ] `stores/notification.js` 通知状态 Store
- [ ] `docker-compose.yml` 五服务编排（Nginx/Django/Celery/MySQL/Redis）
- [ ] Nginx 反向代理配置
- [ ] 前端测试用例（组件渲染/API Mock/用户交互）

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

## 后续计划
- 每周末召开进度同步会议（线上/线下）
- 阶段三目标：4 周内完成全部模块编码
- 阶段四：联调测试 + Bug 修复
- 阶段五：Docker 部署 + 演示准备 + 答辩材料
