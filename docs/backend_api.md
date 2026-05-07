# 后端 RESTful API 接口文档

> OpenAPI 3.0 规范 | 前后端分离 | Base URL: `/api`

## 1. 文档约定

| 项目 | 约定 |
|------|------|
| 协议 | HTTPS（生产）/ HTTP（开发） |
| Base URL | `http://127.0.0.1:8000/api` |
| 认证方式 | Bearer JWT（Header: `Authorization: Bearer <access_token>`） |
| 内容类型 | `application/json`（普通请求）、`multipart/form-data`（文件上传） |
| 响应格式 | `{ "code": 200, "data": {...}, "message": "ok" }` |
| 分页参数 | `?page=1&page_size=20` |
| 错误码 | 400 参数错误、401 未认证、403 无权限、404 不存在、500 服务器错误 |

---

## 2. OpenAPI 3.0 规范（YAML）

```yaml
openapi: "3.0.3"
info:
  title: 软件项目管理平台 API
  description: |
    基于 Django REST Framework 的 RESTful API，支持多项目管理、任务跟踪、
    甘特图、敏捷看板、冲刺管理、工时记录、通知、报表等功能。
  version: "1.0.0"
  contact:
    name: NoStackHub 团队

servers:
  - url: http://127.0.0.1:8000/api
    description: 本地开发环境
  - url: https://example.com/api
    description: 生产环境

# ===================================================
# 安全定义
# ===================================================
security:
  - BearerAuth: []

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: |
        使用 JWT 双令牌机制:
        - Access Token 有效期 30 分钟
        - Refresh Token 有效期 7 天
        - 过期后通过 /api/auth/token/refresh/ 刷新

  # ----- 通用响应 -----
  responses:
    400_BadRequest:
      description: 请求参数校验失败
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: 400
            message: "请求参数错误"
            data: { "name": ["项目名称不能为空"] }
    401_Unauthorized:
      description: 未认证或 Token 过期
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: 401
            message: "认证信息无效或已过期"
    403_Forbidden:
      description: 无操作权限
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: 403
            message: "您没有权限执行此操作"
    404_NotFound:
      description: 资源不存在
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ErrorResponse'
          example:
            code: 404
            message: "未找到请求的资源"

  # ----- 通用 Schema -----
  schemas:
    # 通用响应包装
    SuccessResponse:
      type: object
      properties:
        code:
          type: integer
          example: 200
        message:
          type: string
          example: "ok"
        data:
          type: object
    ErrorResponse:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
        data:
          type: object
          nullable: true
    PaginatedResponse:
      type: object
      properties:
        code:
          type: integer
          example: 200
        message:
          type: string
          example: "ok"
        data:
          type: object
          properties:
            count:
              type: integer
              description: 总记录数
            next:
              type: string
              nullable: true
              description: 下一页 URL
            previous:
              type: string
              nullable: true
              description: 上一页 URL
            results:
              type: array
              items: {}

    # ----- 认证模块 -----
    LoginRequest:
      type: object
      required: [username, password]
      properties:
        username:
          type: string
          minLength: 1
          example: "zhangsan"
        password:
          type: string
          minLength: 6
          format: password
          example: "Abc@123456"
    LoginResponse:
      type: object
      properties:
        access:
          type: string
          description: Access Token
        refresh:
          type: string
          description: Refresh Token
        user:
          $ref: '#/components/schemas/User'

    RegisterRequest:
      type: object
      required: [username, email, password]
      properties:
        username:
          type: string
          minLength: 3
          maxLength: 50
          example: "zhangsan"
        email:
          type: string
          format: email
          maxLength: 100
          example: "zhangsan@example.com"
        password:
          type: string
          minLength: 6
          maxLength: 128
          format: password
          example: "Abc@123456"
        phone:
          type: string
          maxLength: 20
          example: "13800138000"

    TokenRefreshRequest:
      type: object
      required: [refresh]
      properties:
        refresh:
          type: string
          description: Refresh Token

    TokenRefreshResponse:
      type: object
      properties:
        access:
          type: string
        refresh:
          type: string

    # ----- 用户 -----
    User:
      type: object
      properties:
        id:
          type: string
          format: uuid
          example: "550e8400-e29b-41d4-a716-446655440000"
        username:
          type: string
          example: "zhangsan"
        email:
          type: string
          format: email
          example: "zhangsan@example.com"
        phone:
          type: string
          example: "13800138000"
        avatar:
          type: string
          format: uri
          nullable: true
          example: "/media/avatars/default.png"
        role:
          type: string
          enum: [admin, manager, member]
          example: "member"
        is_active:
          type: boolean
          example: true
        created_at:
          type: string
          format: date-time

    UserProfileUpdate:
      type: object
      properties:
        phone:
          type: string
        avatar:
          type: string
          format: binary
          description: 头像文件（multipart）

    # ----- 项目 -----
    Project:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 100
          example: "课程设计项目"
        description:
          type: string
          nullable: true
          example: "软件工程课程设计 - 项目管理平台"
        start_date:
          type: string
          format: date
          example: "2026-03-01"
        end_date:
          type: string
          format: date
          example: "2026-06-30"
        visibility:
          type: string
          enum: [public, private]
          example: "private"
        status:
          type: string
          enum: [planning, active, completed, archived]
          example: "active"
        owner:
          $ref: '#/components/schemas/User'
        member_count:
          type: integer
          example: 8
        task_count:
          type: integer
          example: 45
        progress:
          type: integer
          minimum: 0
          maximum: 100
          description: 项目整体进度百分比
          example: 65
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    ProjectCreate:
      type: object
      required: [name]
      properties:
        name:
          type: string
          maxLength: 100
          example: "新项目"
        description:
          type: string
        start_date:
          type: string
          format: date
          example: "2026-05-01"
        end_date:
          type: string
          format: date
          example: "2026-08-01"
        visibility:
          type: string
          enum: [public, private]
          default: "private"
        template_id:
          type: string
          format: uuid
          description: 项目模板 ID（可选，从模板创建）

    ProjectUpdate:
      type: object
      properties:
        name:
          type: string
          maxLength: 100
        description:
          type: string
        start_date:
          type: string
          format: date
        end_date:
          type: string
          format: date
        visibility:
          type: string
          enum: [public, private]
        status:
          type: string
          enum: [planning, active, completed, archived]

    # ----- 项目成员 -----
    ProjectMember:
      type: object
      properties:
        id:
          type: string
          format: uuid
        user:
          $ref: '#/components/schemas/User'
        role:
          type: string
          enum: [manager, member, viewer]
          example: "member"
        joined_at:
          type: string
          format: date-time

    MemberAdd:
      type: object
      required: [user_id]
      properties:
        user_id:
          type: string
          format: uuid
        role:
          type: string
          enum: [manager, member, viewer]
          default: "member"

    # ----- 项目模板 -----
    ProjectTemplate:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          example: "敏捷开发模板"
        description:
          type: string
          example: "包含默认冲刺、看板列和任务类型的模板"
        config:
          type: object
          description: 模板配置 JSON
        created_by:
          $ref: '#/components/schemas/User'

    # ----- 里程碑 -----
    Milestone:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 100
          example: "需求评审完成"
        description:
          type: string
          nullable: true
        due_date:
          type: string
          format: date
          example: "2026-05-15"
        status:
          type: string
          enum: [pending, completed]
          example: "pending"
        project_id:
          type: string
          format: uuid

    MilestoneCreate:
      type: object
      required: [name, due_date, project_id]
      properties:
        name:
          type: string
          maxLength: 100
        description:
          type: string
        due_date:
          type: string
          format: date
        project_id:
          type: string
          format: uuid

    # ----- 任务 -----
    Task:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
          maxLength: 200
          example: "设计数据库 ER 图"
        description:
          type: string
          nullable: true
          example: "根据需求文档完成 MySQL 数据库 ER 图设计"
        type:
          type: string
          enum: [task, milestone, bug, epic]
          example: "task"
        status:
          type: string
          enum: [todo, in_progress, review, done, blocked]
          example: "in_progress"
        priority:
          type: string
          enum: [low, medium, high, urgent]
          example: "high"
        start_date:
          type: string
          format: date
          example: "2026-05-01"
        due_date:
          type: string
          format: date
          example: "2026-05-07"
        estimated_hours:
          type: number
          format: decimal
          example: 8.0
        actual_hours:
          type: number
          format: decimal
          example: 6.5
        progress:
          type: integer
          minimum: 0
          maximum: 100
          example: 80
        project_id:
          type: string
          format: uuid
        sprint_id:
          type: string
          format: uuid
          nullable: true
        parent_task_id:
          type: string
          format: uuid
          nullable: true
        assignee:
          $ref: '#/components/schemas/User'
        reporter:
          $ref: '#/components/schemas/User'
        subtasks:
          type: array
          items:
            $ref: '#/components/schemas/Task'
          description: 子任务列表
        dependencies:
          type: array
          items:
            $ref: '#/components/schemas/TaskDependency'
          description: 任务依赖列表
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    TaskCreate:
      type: object
      required: [title, project_id]
      properties:
        title:
          type: string
          maxLength: 200
        description:
          type: string
        type:
          type: string
          enum: [task, milestone, bug, epic]
          default: "task"
        priority:
          type: string
          enum: [low, medium, high, urgent]
          default: "medium"
        start_date:
          type: string
          format: date
        due_date:
          type: string
          format: date
        estimated_hours:
          type: number
          format: decimal
          example: 8.0
        project_id:
          type: string
          format: uuid
        sprint_id:
          type: string
          format: uuid
        parent_task_id:
          type: string
          format: uuid
        assignee_id:
          type: string
          format: uuid
          description: 负责人用户 ID

    TaskUpdate:
      type: object
      properties:
        title:
          type: string
          maxLength: 200
        description:
          type: string
        type:
          type: string
          enum: [task, milestone, bug, epic]
        priority:
          type: string
          enum: [low, medium, high, urgent]
        start_date:
          type: string
          format: date
        due_date:
          type: string
          format: date
        estimated_hours:
          type: number
        sprint_id:
          type: string
          format: uuid
        parent_task_id:
          type: string
          format: uuid
        assignee_id:
          type: string
          format: uuid

    TaskStatusUpdate:
      type: object
      required: [status]
      properties:
        status:
          type: string
          enum: [todo, in_progress, review, done, blocked]
          example: "review"

    # ----- 任务依赖 -----
    TaskDependency:
      type: object
      properties:
        id:
          type: string
          format: uuid
        predecessor:
          type: object
          properties:
            id:
              type: string
              format: uuid
            title:
              type: string
            status:
              type: string
        successor:
          type: object
          properties:
            id:
              type: string
              format: uuid
            title:
              type: string
            status:
              type: string
        relation_type:
          type: string
          enum: [blocks, precedes, relates_to]
          example: "precedes"
        created_at:
          type: string
          format: date-time

    TaskDependencyCreate:
      type: object
      required: [successor_id]
      properties:
        successor_id:
          type: string
          format: uuid
          description: 后继任务 ID
        relation_type:
          type: string
          enum: [blocks, precedes, relates_to]
          default: "precedes"

    # ----- 看板 -----
    KanbanBoard:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 100
          example: "团队看板"
        type:
          type: string
          enum: [team, version, sub_project]
          example: "team"
        project_id:
          type: string
          format: uuid
        columns:
          type: array
          items:
            $ref: '#/components/schemas/KanbanColumn'
        created_at:
          type: string
          format: date-time

    KanbanBoardCreate:
      type: object
      required: [name, project_id]
      properties:
        name:
          type: string
          maxLength: 100
        type:
          type: string
          enum: [team, version, sub_project]
          default: "team"
        project_id:
          type: string
          format: uuid

    KanbanColumn:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 50
          example: "进行中"
        order:
          type: integer
          example: 1
        wip_limit:
          type: integer
          example: 5
          description: 在制品限制，0 表示无限制
        board_id:
          type: string
          format: uuid
        tasks:
          type: array
          items:
            $ref: '#/components/schemas/Task'
          description: 该列中的任务列表

    KanbanColumnCreate:
      type: object
      required: [name]
      properties:
        name:
          type: string
          maxLength: 50
        order:
          type: integer
        wip_limit:
          type: integer
          default: 0
        board_id:
          type: string
          format: uuid

    KanbanTaskMove:
      type: object
      required: [task_id, target_column_id]
      properties:
        task_id:
          type: string
          format: uuid
        target_column_id:
          type: string
          format: uuid
        order:
          type: integer
          description: 目标列中的位置序号

    # ----- 冲刺 -----
    Sprint:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          maxLength: 100
          example: "Sprint 1"
        goal:
          type: string
          nullable: true
          example: "完成用户认证模块"
        start_date:
          type: string
          format: date
          example: "2026-05-01"
        end_date:
          type: string
          format: date
          example: "2026-05-14"
        status:
          type: string
          enum: [planning, active, completed]
          example: "active"
        project_id:
          type: string
          format: uuid
        tasks:
          type: array
          items:
            $ref: '#/components/schemas/Task'
        total_estimated:
          type: number
          description: 总预估工时
        total_actual:
          type: number
          description: 总实际工时
        progress:
          type: integer
          example: 60
        created_at:
          type: string
          format: date-time

    SprintCreate:
      type: object
      required: [name, start_date, end_date, project_id]
      properties:
        name:
          type: string
          maxLength: 100
        goal:
          type: string
        start_date:
          type: string
          format: date
        end_date:
          type: string
          format: date
        project_id:
          type: string
          format: uuid

    SprintUpdate:
      type: object
      properties:
        name:
          type: string
        goal:
          type: string
        start_date:
          type: string
          format: date
        end_date:
          type: string
          format: date

    SprintTaskManage:
      type: object
      required: [task_id]
      properties:
        task_id:
          type: string
          format: uuid

    BurndownData:
      type: object
      properties:
        sprint:
          $ref: '#/components/schemas/Sprint'
        ideal_line:
          type: array
          items:
            type: object
            properties:
              date: { type: string, format: date }
              remaining: { type: number }
        actual_line:
          type: array
          items:
            type: object
            properties:
              date: { type: string, format: date }
              remaining: { type: number }

    # ----- 工时 -----
    WorkLog:
      type: object
      properties:
        id:
          type: string
          format: uuid
        task_id:
          type: string
          format: uuid
        task_title:
          type: string
        user:
          $ref: '#/components/schemas/User'
        hours:
          type: number
          format: decimal
          example: 4.5
        date:
          type: string
          format: date
          example: "2026-05-06"
        description:
          type: string
          nullable: true
          example: "完成 ER 图设计并评审"
        created_at:
          type: string
          format: date-time

    WorkLogCreate:
      type: object
      required: [task_id, hours, date]
      properties:
        task_id:
          type: string
          format: uuid
        hours:
          type: number
          format: decimal
          minimum: 0.25
          maximum: 24
          example: 4.5
        date:
          type: string
          format: date
        description:
          type: string

    WorkLogUpdate:
      type: object
      properties:
        hours:
          type: number
        date:
          type: string
          format: date
        description:
          type: string

    WorkLogSummary:
      type: object
      properties:
        total_hours:
          type: number
          example: 160.5
        by_user:
          type: array
          items:
            type: object
            properties:
              user_id: { type: string, format: uuid }
              username: { type: string }
              hours: { type: number }
        by_date:
          type: array
          items:
            type: object
            properties:
              date: { type: string, format: date }
              hours: { type: number }

    # ----- 评论 -----
    Comment:
      type: object
      properties:
        id:
          type: string
          format: uuid
        content:
          type: string
          example: "ER 图需要补充索引设计"
        author:
          $ref: '#/components/schemas/User'
        task_id:
          type: string
          format: uuid
          nullable: true
        project_id:
          type: string
          format: uuid
          nullable: true
        parent_comment_id:
          type: string
          format: uuid
          nullable: true
          description: 父评论 ID（回复时使用）
        replies:
          type: array
          items:
            $ref: '#/components/schemas/Comment'
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    CommentCreate:
      type: object
      required: [content]
      properties:
        content:
          type: string
        parent_comment_id:
          type: string
          format: uuid
          description: 回复某条评论时传入

    # ----- 通知 -----
    Notification:
      type: object
      properties:
        id:
          type: string
          format: uuid
        type:
          type: string
          enum:
            - task_assigned
            - status_change
            - comment
            - deadline
            - mention
            - project_invite
            - sprint_start
            - sprint_end
          example: "task_assigned"
        title:
          type: string
          example: "新任务分配"
        content:
          type: string
          example: "张三 将任务「设计数据库 ER 图」分配给了您"
        is_read:
          type: boolean
          example: false
        related_type:
          type: string
          example: "Task"
        related_id:
          type: string
          format: uuid
        created_at:
          type: string
          format: date-time

    # ----- 附件 -----
    Attachment:
      type: object
      properties:
        id:
          type: string
          format: uuid
        filename:
          type: string
          example: "er-diagram-v2.png"
        file_path:
          type: string
          example: "/media/attachments/2026/05/er-diagram-v2.png"
        file_size:
          type: integer
          example: 245760
        mime_type:
          type: string
          example: "image/png"
        task_id:
          type: string
          format: uuid
          nullable: true
        project_id:
          type: string
          format: uuid
          nullable: true
        uploader:
          $ref: '#/components/schemas/User'
        uploaded_at:
          type: string
          format: date-time

    # ----- 报表 -----
    Report:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          example: "Sprint 1 进度报告"
        type:
          type: string
          enum: [task_list, worklog_summary, gantt, progress, burndown]
          example: "progress"
        project_id:
          type: string
          format: uuid
        generated_by:
          $ref: '#/components/schemas/User'
        parameters:
          type: object
          description: 生成参数 JSON（时间范围、筛选条件等）
        file_path:
          type: string
          nullable: true
          description: 导出文件下载路径
        created_at:
          type: string
          format: date-time

    ReportGenerate:
      type: object
      required: [type, project_id]
      properties:
        name:
          type: string
        type:
          type: string
          enum: [task_list, worklog_summary, gantt, progress, burndown]
        project_id:
          type: string
          format: uuid
        parameters:
          type: object
          properties:
            start_date: { type: string, format: date }
            end_date: { type: string, format: date }
            sprint_id: { type: string, format: uuid }
            format: { type: string, enum: [pdf, excel, csv], default: "pdf" }

    # ----- 甘特图 -----
    GanttData:
      type: object
      properties:
        tasks:
          type: array
          items:
            type: object
            properties:
              id: { type: string, format: uuid }
              title: { type: string }
              start_date: { type: string, format: date }
              due_date: { type: string, format: date }
              progress: { type: integer }
              assignee: { type: string }
              dependencies:
                type: array
                items:
                  type: object
                  properties:
                    predecessor_id: { type: string, format: uuid }
                    type: { type: string }
        milestones:
          type: array
          items:
            $ref: '#/components/schemas/Milestone'

    # ----- 仪表盘 -----
    Dashboard:
      type: object
      properties:
        id:
          type: string
          format: uuid
        name:
          type: string
          example: "我的工作台"
        config:
          type: object
          description: 布局与小组件配置
        user_id:
          type: string
          format: uuid
        is_default:
          type: boolean
        created_at:
          type: string
          format: date-time

    # ----- 活动日志 -----
    ActivityLog:
      type: object
      properties:
        id:
          type: string
          format: uuid
        entity_type:
          type: string
          example: "Task"
        entity_id:
          type: string
          format: uuid
        field_name:
          type: string
          example: "status"
        old_value:
          type: string
          nullable: true
          example: "todo"
        new_value:
          type: string
          nullable: true
          example: "in_progress"
        changed_by:
          $ref: '#/components/schemas/User'
        changed_at:
          type: string
          format: date-time

  # ----- 请求参数 -----
  parameters:
    ProjectID:
      name: project_id
      in: query
      schema:
        type: string
        format: uuid
      description: 按项目 ID 筛选
    Status:
      name: status
      in: query
      schema:
        type: string
      description: 按状态筛选
    AssigneeID:
      name: assignee_id
      in: query
      schema:
        type: string
        format: uuid
      description: 按负责人 ID 筛选
    SprintID:
      name: sprint_id
      in: query
      schema:
        type: string
        format: uuid
      description: 按冲刺 ID 筛选
    Priority:
      name: priority
      in: query
      schema:
        type: string
        enum: [low, medium, high, urgent]
    Search:
      name: search
      in: query
      schema:
        type: string
      description: 关键词搜索（标题、描述）
    Ordering:
      name: ordering
      in: query
      schema:
        type: string
      description: "排序字段，前缀 - 表示降序。例: -created_at, due_date"
    Page:
      name: page
      in: query
      schema:
        type: integer
        default: 1
    PageSize:
      name: page_size
      in: query
      schema:
        type: integer
        default: 20
        maximum: 100

# ===================================================
# API 路径定义
# ===================================================
paths:

  # ========== 1. 认证模块 /api/auth ==========
  /auth/login/:
    post:
      tags: [1-认证 Auth]
      summary: 用户登录
      description: 使用用户名和密码登录，返回 JWT 双令牌
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/LoginRequest'
      responses:
        '200':
          description: 登录成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/LoginResponse'
        '400': { $ref: '#/components/responses/400_BadRequest' }

  /auth/register/:
    post:
      tags: [1-认证 Auth]
      summary: 用户注册
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegisterRequest'
      responses:
        '201':
          description: 注册成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/LoginResponse'
        '400': { $ref: '#/components/responses/400_BadRequest' }

  /auth/token/refresh/:
    post:
      tags: [1-认证 Auth]
      summary: 刷新 Access Token
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TokenRefreshRequest'
      responses:
        '200':
          description: 刷新成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/TokenRefreshResponse'

  /auth/profile/:
    get:
      tags: [1-认证 Auth]
      summary: 获取当前用户信息
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/User'
    put:
      tags: [1-认证 Auth]
      summary: 更新个人信息
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserProfileUpdate'
      responses:
        '200':
          description: 更新成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/User'

  /auth/change-password/:
    post:
      tags: [1-认证 Auth]
      summary: 修改密码
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [old_password, new_password]
              properties:
                old_password:
                  type: string
                  format: password
                new_password:
                  type: string
                  format: password
                  minLength: 6
      responses:
        '200':
          description: 密码修改成功

  # ========== 2. 项目模块 /api/projects ==========
  /projects/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目列表
      description: 返回当前用户参与的所有项目，支持筛选与分页
      parameters:
        - $ref: '#/components/parameters/Status'
        - $ref: '#/components/parameters/Search'
        - $ref: '#/components/parameters/Ordering'
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/PageSize'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/Project'
    post:
      tags: [2-项目 Projects]
      summary: 创建项目
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectCreate'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Project'
        '400': { $ref: '#/components/responses/400_BadRequest' }

  /projects/{id}/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目详情
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Project'
        '404': { $ref: '#/components/responses/404_NotFound' }
    put:
      tags: [2-项目 Projects]
      summary: 更新项目信息
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ProjectUpdate'
      responses:
        '200':
          description: 更新成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Project'
    delete:
      tags: [2-项目 Projects]
      summary: 删除项目
      description: 仅项目负责人可删除
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 删除成功
        '403': { $ref: '#/components/responses/403_Forbidden' }

  /projects/{id}/members/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目成员列表
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/ProjectMember'
    post:
      tags: [2-项目 Projects]
      summary: 添加项目成员
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MemberAdd'
      responses:
        '201':
          description: 添加成功

  /projects/{id}/members/{member_id}/:
    put:
      tags: [2-项目 Projects]
      summary: 更新成员角色
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: member_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                role:
                  type: string
                  enum: [manager, member, viewer]
      responses:
        '200':
          description: 更新成功
    delete:
      tags: [2-项目 Projects]
      summary: 移除项目成员
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: member_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 移除成功

  /projects/{id}/milestones/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目里程碑列表
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/Milestone'
    post:
      tags: [2-项目 Projects]
      summary: 创建里程碑
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/MilestoneCreate'
      responses:
        '201':
          description: 创建成功

  /projects/{id}/milestones/{milestone_id}/:
    put:
      tags: [2-项目 Projects]
      summary: 更新里程碑
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: milestone_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 更新成功
    delete:
      tags: [2-项目 Projects]
      summary: 删除里程碑
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: milestone_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /projects/{id}/gantt/:
    get:
      tags: [2-项目 Projects]
      summary: 获取甘特图数据
      description: 返回项目所有任务的时间线、依赖关系和里程碑
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/GanttData'

  /projects/{id}/activity/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目活动日志
      description: 返回项目的变更记录时间线
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/PageSize'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/ActivityLog'

  # ----- 项目模板 -----
  /projects/templates/:
    get:
      tags: [2-项目 Projects]
      summary: 获取项目模板列表
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/ProjectTemplate'
    post:
      tags: [2-项目 Projects]
      summary: 创建项目模板
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name, config]
              properties:
                name: { type: string }
                description: { type: string }
                config: { type: object }
      responses:
        '201':
          description: 创建成功

  # ========== 3. 任务模块 /api/tasks ==========
  /tasks/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务列表
      description: 支持多维度筛选，默认分页返回
      parameters:
        - $ref: '#/components/parameters/ProjectID'
        - $ref: '#/components/parameters/Status'
        - $ref: '#/components/parameters/Priority'
        - $ref: '#/components/parameters/AssigneeID'
        - $ref: '#/components/parameters/SprintID'
        - $ref: '#/components/parameters/Search'
        - $ref: '#/components/parameters/Ordering'
        - $ref: '#/components/parameters/Page'
        - $ref: '#/components/parameters/PageSize'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/Task'
    post:
      tags: [3-任务 Tasks]
      summary: 创建任务
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskCreate'
      responses:
        '201':
          description: 创建成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Task'

  /tasks/{id}/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务详情
      description: 包含子任务、依赖关系和评论
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Task'
    put:
      tags: [3-任务 Tasks]
      summary: 更新任务信息
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskUpdate'
      responses:
        '200':
          description: 更新成功
    delete:
      tags: [3-任务 Tasks]
      summary: 删除任务
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /tasks/{id}/status/:
    patch:
      tags: [3-任务 Tasks]
      summary: 更新任务状态
      description: 看板拖拽时的状态变更接口，自动记录变更日志并发送通知
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskStatusUpdate'
      responses:
        '200':
          description: 状态更新成功

  /tasks/{id}/dependencies/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务依赖列表
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/TaskDependency'
    post:
      tags: [3-任务 Tasks]
      summary: 添加任务依赖
      description: 为当前任务（作为前驱）添加后继依赖
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/TaskDependencyCreate'
      responses:
        '201':
          description: 添加成功

  /tasks/{id}/dependencies/{dep_id}/:
    delete:
      tags: [3-任务 Tasks]
      summary: 移除任务依赖
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: dep_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 移除成功

  /tasks/{id}/comments/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务评论列表
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - $ref: '#/components/parameters/Page'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/Comment'
    post:
      tags: [3-任务 Tasks]
      summary: 添加评论
      description: 支持 @提及用户（在 content 中使用 @username 语法）
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CommentCreate'
      responses:
        '201':
          description: 添加成功

  /tasks/{id}/attachments/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务附件列表
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/Attachment'
    post:
      tags: [3-任务 Tasks]
      summary: 上传任务附件
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                  description: "文件, 最大 50MB"
      responses:
        '201':
          description: 上传成功

  /tasks/{id}/worklogs/:
    get:
      tags: [3-任务 Tasks]
      summary: 获取任务工时记录
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/WorkLog'

  # ========== 4. 看板模块 /api/boards ==========
  /boards/:
    get:
      tags: [4-看板 Kanban]
      summary: 获取看板列表
      parameters:
        - $ref: '#/components/parameters/ProjectID'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/KanbanBoard'
    post:
      tags: [4-看板 Kanban]
      summary: 创建看板
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/KanbanBoardCreate'
      responses:
        '201':
          description: 创建成功

  /boards/{id}/:
    get:
      tags: [4-看板 Kanban]
      summary: 获取看板详情（含所有列及列内任务）
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/KanbanBoard'
    delete:
      tags: [4-看板 Kanban]
      summary: 删除看板
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /boards/{id}/columns/:
    get:
      tags: [4-看板 Kanban]
      summary: 获取看板的所有列
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/KanbanColumn'
    post:
      tags: [4-看板 Kanban]
      summary: 添加看板列
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/KanbanColumnCreate'
      responses:
        '201':
          description: 添加成功

  /boards/{id}/columns/{column_id}/:
    put:
      tags: [4-看板 Kanban]
      summary: 更新看板列
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: column_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name: { type: string }
                wip_limit: { type: integer }
      responses:
        '200':
          description: 更新成功
    delete:
      tags: [4-看板 Kanban]
      summary: 删除看板列
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: column_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /boards/{id}/move-task/:
    post:
      tags: [4-看板 Kanban]
      summary: 移动任务到指定列
      description: 看板拖拽核心接口，移动任务并自动更新任务状态
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/KanbanTaskMove'
      responses:
        '200':
          description: 移动成功

  # ========== 5. 冲刺模块 /api/sprints ==========
  /sprints/:
    get:
      tags: [5-冲刺 Sprints]
      summary: 获取冲刺列表
      parameters:
        - $ref: '#/components/parameters/ProjectID'
        - $ref: '#/components/parameters/Status'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/Sprint'
    post:
      tags: [5-冲刺 Sprints]
      summary: 创建冲刺
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SprintCreate'
      responses:
        '201':
          description: 创建成功

  /sprints/{id}/:
    get:
      tags: [5-冲刺 Sprints]
      summary: 获取冲刺详情（含任务列表）
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Sprint'
    put:
      tags: [5-冲刺 Sprints]
      summary: 更新冲刺信息
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SprintUpdate'
      responses:
        '200':
          description: 更新成功
    delete:
      tags: [5-冲刺 Sprints]
      summary: 删除冲刺
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /sprints/{id}/start/:
    post:
      tags: [5-冲刺 Sprints]
      summary: 启动冲刺
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 启动成功（status → active）

  /sprints/{id}/complete/:
    post:
      tags: [5-冲刺 Sprints]
      summary: 完成冲刺
      description: 将未完成任务移回 Backlog，归档冲刺
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 完成成功（status → completed）

  /sprints/{id}/tasks/:
    post:
      tags: [5-冲刺 Sprints]
      summary: 向冲刺添加任务
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/SprintTaskManage'
      responses:
        '200':
          description: 添加成功

  /sprints/{id}/tasks/{task_id}/:
    delete:
      tags: [5-冲刺 Sprints]
      summary: 从冲刺移除任务
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: task_id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 移除成功

  /sprints/{id}/burndown/:
    get:
      tags: [5-冲刺 Sprints]
      summary: 获取燃尽图数据
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/BurndownData'

  # ========== 6. 工时模块 /api/worklogs ==========
  /worklogs/:
    get:
      tags: [6-工时 WorkLogs]
      summary: 获取工时记录列表
      parameters:
        - $ref: '#/components/parameters/ProjectID'
        - name: task_id
          in: query
          schema: { type: string, format: uuid }
        - name: user_id
          in: query
          schema: { type: string, format: uuid }
        - name: start_date
          in: query
          schema: { type: string, format: date }
        - name: end_date
          in: query
          schema: { type: string, format: date }
        - $ref: '#/components/parameters/Page'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/WorkLog'
    post:
      tags: [6-工时 WorkLogs]
      summary: 记录工时
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkLogCreate'
      responses:
        '201':
          description: 记录成功

  /worklogs/{id}/:
    put:
      tags: [6-工时 WorkLogs]
      summary: 修改工时记录
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WorkLogUpdate'
      responses:
        '200':
          description: 修改成功
    delete:
      tags: [6-工时 WorkLogs]
      summary: 删除工时记录
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  /worklogs/summary/:
    get:
      tags: [6-工时 WorkLogs]
      summary: 获取工时汇总统计
      description: 按项目/用户/日期范围汇总工时
      parameters:
        - name: project_id
          in: query
          required: true
          schema: { type: string, format: uuid }
        - name: start_date
          in: query
          schema: { type: string, format: date }
        - name: end_date
          in: query
          schema: { type: string, format: date }
        - name: user_id
          in: query
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/WorkLogSummary'

  # ========== 7. 通知模块 /api/notifications ==========
  /notifications/:
    get:
      tags: [7-通知 Notifications]
      summary: 获取通知列表
      parameters:
        - name: is_read
          in: query
          schema:
            type: boolean
          description: "筛选: true=已读, false=未读, 不传=全部"
        - $ref: '#/components/parameters/Page'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/Notification'
                          unread_count:
                            type: integer
                            description: 未读通知总数

  /notifications/{id}/read/:
    post:
      tags: [7-通知 Notifications]
      summary: 标记单条通知已读
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 标记成功

  /notifications/read-all/:
    post:
      tags: [7-通知 Notifications]
      summary: 标记全部通知已读
      responses:
        '200':
          description: 全部标记成功

  # ========== 8. 报表模块 /api/reports ==========
  /reports/:
    get:
      tags: [8-报表 Reports]
      summary: 获取报表历史
      parameters:
        - $ref: '#/components/parameters/ProjectID'
        - $ref: '#/components/parameters/Page'
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/PaginatedResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          results:
                            type: array
                            items:
                              $ref: '#/components/schemas/Report'
    post:
      tags: [8-报表 Reports]
      summary: 生成报表
      description: 异步任务，返回报表 ID，通过 GET /reports/{id}/ 查询生成状态
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ReportGenerate'
      responses:
        '202':
          description: 报表生成任务已提交
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: object
                        properties:
                          report_id:
                            type: string
                            format: uuid
                            description: 用于轮询生成状态

  /reports/{id}/:
    get:
      tags: [8-报表 Reports]
      summary: 获取报表详情 / 查询生成状态
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 成功（若已生成则包含下载链接）
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Report'

  /reports/{id}/download/:
    get:
      tags: [8-报表 Reports]
      summary: 下载报表文件
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 文件流
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary

  # ========== 9. 文件模块 /api/files ==========
  /files/:
    post:
      tags: [9-文件 Files]
      summary: 上传文件（通用）
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              required: [file]
              properties:
                file:
                  type: string
                  format: binary
                task_id:
                  type: string
                  format: uuid
                project_id:
                  type: string
                  format: uuid
      responses:
        '201':
          description: 上传成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        $ref: '#/components/schemas/Attachment'

  /files/{id}/:
    get:
      tags: [9-文件 Files]
      summary: 下载文件
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 文件流
          content:
            application/octet-stream:
              schema:
                type: string
                format: binary
    delete:
      tags: [9-文件 Files]
      summary: 删除文件
      parameters:
        - name: id
          in: path
          required: true
          schema: { type: string, format: uuid }
      responses:
        '200':
          description: 删除成功

  # ========== 10. 仪表盘模块 /api/dashboards ==========
  /dashboards/:
    get:
      tags: [10-仪表盘 Dashboard]
      summary: 获取我的仪表盘列表
      responses:
        '200':
          description: 成功
          content:
            application/json:
              schema:
                allOf:
                  - $ref: '#/components/schemas/SuccessResponse'
                  - type: object
                    properties:
                      data:
                        type: array
                        items:
                          $ref: '#/components/schemas/Dashboard'
    post:
      tags: [10-仪表盘 Dashboard]
      summary: 创建自定义仪表盘
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [name, config]
              properties:
                name: { type: string }
                config: { type: object }
                is_default: { type: boolean, default: false }
      responses:
        '201':
          description: 创建成功
```

---

## 3. 接口汇总表

| 模块 | 方法 | 端点 | 说明 |
|------|------|------|------|
| 认证 | POST | `/auth/login/` | 用户登录 |
| 认证 | POST | `/auth/register/` | 用户注册 |
| 认证 | POST | `/auth/token/refresh/` | 刷新 Token |
| 认证 | GET | `/auth/profile/` | 获取个人信息 |
| 认证 | PUT | `/auth/profile/` | 更新个人信息 |
| 认证 | POST | `/auth/change-password/` | 修改密码 |
| 项目 | GET | `/projects/` | 项目列表 |
| 项目 | POST | `/projects/` | 创建项目 |
| 项目 | GET | `/projects/{id}/` | 项目详情 |
| 项目 | PUT | `/projects/{id}/` | 更新项目 |
| 项目 | DELETE | `/projects/{id}/` | 删除项目 |
| 项目 | GET | `/projects/{id}/members/` | 成员列表 |
| 项目 | POST | `/projects/{id}/members/` | 添加成员 |
| 项目 | PUT | `/projects/{id}/members/{mid}/` | 更新成员角色 |
| 项目 | DELETE | `/projects/{id}/members/{mid}/` | 移除成员 |
| 项目 | GET | `/projects/{id}/milestones/` | 里程碑列表 |
| 项目 | POST | `/projects/{id}/milestones/` | 创建里程碑 |
| 项目 | GET | `/projects/{id}/gantt/` | 甘特图数据 |
| 项目 | GET | `/projects/{id}/activity/` | 活动日志 |
| 项目 | GET | `/projects/templates/` | 模板列表 |
| 任务 | GET | `/tasks/` | 任务列表 |
| 任务 | POST | `/tasks/` | 创建任务 |
| 任务 | GET | `/tasks/{id}/` | 任务详情 |
| 任务 | PUT | `/tasks/{id}/` | 更新任务 |
| 任务 | DELETE | `/tasks/{id}/` | 删除任务 |
| 任务 | PATCH | `/tasks/{id}/status/` | 更新任务状态 |
| 任务 | GET | `/tasks/{id}/dependencies/` | 依赖列表 |
| 任务 | POST | `/tasks/{id}/dependencies/` | 添加依赖 |
| 任务 | DELETE | `/tasks/{id}/dependencies/{did}/` | 移除依赖 |
| 任务 | GET | `/tasks/{id}/comments/` | 评论列表 |
| 任务 | POST | `/tasks/{id}/comments/` | 添加评论 |
| 任务 | GET | `/tasks/{id}/attachments/` | 附件列表 |
| 任务 | POST | `/tasks/{id}/attachments/` | 上传附件 |
| 看板 | GET | `/boards/` | 看板列表 |
| 看板 | POST | `/boards/` | 创建看板 |
| 看板 | GET | `/boards/{id}/` | 看板详情 |
| 看板 | DELETE | `/boards/{id}/` | 删除看板 |
| 看板 | GET | `/boards/{id}/columns/` | 列列表 |
| 看板 | POST | `/boards/{id}/columns/` | 添加列 |
| 看板 | PUT | `/boards/{id}/columns/{cid}/` | 更新列 |
| 看板 | DELETE | `/boards/{id}/columns/{cid}/` | 删除列 |
| 看板 | POST | `/boards/{id}/move-task/` | 移动任务 |
| 冲刺 | GET | `/sprints/` | 冲刺列表 |
| 冲刺 | POST | `/sprints/` | 创建冲刺 |
| 冲刺 | GET | `/sprints/{id}/` | 冲刺详情 |
| 冲刺 | PUT | `/sprints/{id}/` | 更新冲刺 |
| 冲刺 | DELETE | `/sprints/{id}/` | 删除冲刺 |
| 冲刺 | POST | `/sprints/{id}/start/` | 启动冲刺 |
| 冲刺 | POST | `/sprints/{id}/complete/` | 完成冲刺 |
| 冲刺 | POST | `/sprints/{id}/tasks/` | 添加任务 |
| 冲刺 | DELETE | `/sprints/{id}/tasks/{tid}/` | 移除任务 |
| 冲刺 | GET | `/sprints/{id}/burndown/` | 燃尽图数据 |
| 工时 | GET | `/worklogs/` | 工时列表 |
| 工时 | POST | `/worklogs/` | 记录工时 |
| 工时 | PUT | `/worklogs/{id}/` | 修改工时 |
| 工时 | DELETE | `/worklogs/{id}/` | 删除工时 |
| 工时 | GET | `/worklogs/summary/` | 工时汇总 |
| 通知 | GET | `/notifications/` | 通知列表（含未读数） |
| 通知 | POST | `/notifications/{id}/read/` | 标记已读 |
| 通知 | POST | `/notifications/read-all/` | 全部已读 |
| 报表 | GET | `/reports/` | 报表历史 |
| 报表 | POST | `/reports/` | 生成报表（异步） |
| 报表 | GET | `/reports/{id}/` | 报表状态/详情 |
| 报表 | GET | `/reports/{id}/download/` | 下载报表 |
| 文件 | POST | `/files/` | 上传文件 |
| 文件 | GET | `/files/{id}/` | 下载文件 |
| 文件 | DELETE | `/files/{id}/` | 删除文件 |
| 仪表盘 | GET | `/dashboards/` | 仪表盘列表 |
| 仪表盘 | POST | `/dashboards/` | 创建仪表盘 |

**总计：60+ 个 RESTful 接口**，覆盖 10 个功能模块。

---

## 4. 通用查询参数

所有列表类接口（GET）统一支持以下参数：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|------|------|
| `page` | int | 1 | 页码 |
| `page_size` | int | 20 | 每页条数（最大 100） |
| `ordering` | string | - | 排序字段，前缀 `-` 表示降序 |
| `search` | string | - | 关键词搜索 |
| `project_id` | uuid | - | 按项目筛选 |
| `status` | string | - | 按状态筛选 |

---

## 5. 错误码规范

| HTTP 状态码 | code | 说明 |
|-------------|------|------|
| 200 | 200 | 请求成功 |
| 201 | 201 | 创建成功 |
| 400 | 400 | 参数校验失败 |
| 401 | 401 | Token 无效或过期 |
| 403 | 403 | 无操作权限 |
| 404 | 404 | 资源不存在 |
| 413 | 413 | 文件大小超过限制 |
| 500 | 500 | 服务器内部错误 |

---

## 6. 前后端协作约定

1. **认证**：前端存储 Access Token + Refresh Token 到 localStorage，Axios 拦截器自动附带 Bearer Token；Token 过期自动无感刷新
2. **分页**：统一使用 `page` + `page_size` 参数，响应中 `count` / `next` / `previous` 用于前端分页组件
3. **文件上传**：使用 `multipart/form-data` 编码，`/tasks/{id}/attachments/` 或 `/files/` 通用上传接口
4. **实时通知**：通知模块通过前端轮询 `/notifications/?is_read=false` 实现（后续可升级 WebSocket）
5. **乐观更新**：看板拖拽等高频操作，前端先更新 UI 状态，再调用 API 确认；若失败则回滚 UI
6. **API 文档**：已集成 `drf-spectacular`，开发环境访问 `http://127.0.0.1:8000/api/docs/` 查看 Swagger UI
