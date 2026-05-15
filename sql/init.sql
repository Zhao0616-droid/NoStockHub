-- ===================================================
-- 软件项目管理平台 - 数据库初始化脚本
-- 基于架构文档 architect.md 中的 ER 图生成
-- 数据库: MySQL 8.0+ | 字符集: utf8mb4
-- ===================================================
--
-- 维护约定（与 Django 对齐）：
-- • accounts_*、notifications_* 等由 Django migrations 创建，请勿在此 CREATE。
-- • 以下为历史/占位 DDL，仅存数据列与外键到外键已由 Django 负责的表；
--   不在此声明指向 accounts_user 的外键，避免 MySQL 在 migrate 前就要求用户表必须先存在。
-- • 若本地曾用旧版 init.sql 建过 notifications_notification，迁移前请先 DROP TABLE
--   notifications_notification（或清空 volume），避免与 Django 建表冲突。
-- ===================================================

CREATE DATABASE IF NOT EXISTS project_platform
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE project_platform;

-- ===================================================
-- 1. 用户与权限模块 → 全部由 Django migrations 管理（accounts_role / accounts_user 等）
-- ===================================================

-- ===================================================
-- 2. 项目管理模块
-- ===================================================

-- 项目模板表
CREATE TABLE IF NOT EXISTS projects_projecttemplate (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    config JSON NOT NULL COMMENT '模板配置: 默认阶段、看板列、任务类型等',
    created_by CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 项目表
CREATE TABLE IF NOT EXISTS projects_project (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE,
    end_date DATE,
    visibility ENUM('public', 'private') DEFAULT 'private',
    status ENUM('planning', 'active', 'completed', 'archived') DEFAULT 'planning',
    owner_id CHAR(36) NOT NULL,
    template_id CHAR(36) DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES projects_projecttemplate(id) ON DELETE SET NULL,
    INDEX idx_project_status (status),
    INDEX idx_project_owner (owner_id)
) ENGINE=InnoDB;

-- 项目成员表
CREATE TABLE IF NOT EXISTS projects_projectmember (
    id CHAR(36) PRIMARY KEY,
    project_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    role ENUM('manager', 'member', 'viewer') DEFAULT 'member',
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_project_user (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 里程碑表
CREATE TABLE IF NOT EXISTS projects_milestone (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status ENUM('pending', 'completed') DEFAULT 'pending',
    project_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    INDEX idx_milestone_project (project_id)
) ENGINE=InnoDB;

-- ===================================================
-- 3. 冲刺模块
-- ===================================================

CREATE TABLE IF NOT EXISTS sprints_sprint (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    goal TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('planning', 'active', 'completed') DEFAULT 'planning',
    project_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    INDEX idx_sprint_project (project_id),
    INDEX idx_sprint_status (status)
) ENGINE=InnoDB;

-- ===================================================
-- 4. 任务管理模块
-- ===================================================

-- 任务表
CREATE TABLE IF NOT EXISTS tasks_task (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type ENUM('task', 'milestone', 'bug', 'epic') DEFAULT 'task',
    status ENUM('todo', 'in_progress', 'review', 'done', 'blocked') DEFAULT 'todo',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    start_date DATE,
    due_date DATE,
    estimated_hours DECIMAL(8,2) DEFAULT 0.00,
    actual_hours DECIMAL(8,2) DEFAULT 0.00,
    progress INT DEFAULT 0 COMMENT '进度百分比 0-100',
    project_id CHAR(36) NOT NULL,
    sprint_id CHAR(36) DEFAULT NULL,
    parent_task_id CHAR(36) DEFAULT NULL,
    assignee_id CHAR(36) DEFAULT NULL,
    reporter_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    FOREIGN KEY (sprint_id) REFERENCES sprints_sprint(id) ON DELETE SET NULL,
    FOREIGN KEY (parent_task_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    INDEX idx_task_project (project_id),
    INDEX idx_task_sprint (sprint_id),
    INDEX idx_task_assignee (assignee_id),
    INDEX idx_task_status (status),
    INDEX idx_task_priority (priority),
    INDEX idx_task_parent (parent_task_id)
) ENGINE=InnoDB;

-- 任务依赖表
CREATE TABLE IF NOT EXISTS tasks_taskdependency (
    id CHAR(36) PRIMARY KEY,
    predecessor_id CHAR(36) NOT NULL COMMENT '前驱任务',
    successor_id CHAR(36) NOT NULL COMMENT '后继任务',
    relation_type ENUM('blocks', 'precedes', 'relates_to') DEFAULT 'precedes',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_dependency (predecessor_id, successor_id),
    FOREIGN KEY (predecessor_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    FOREIGN KEY (successor_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    INDEX idx_dep_predecessor (predecessor_id),
    INDEX idx_dep_successor (successor_id)
) ENGINE=InnoDB;

-- ===================================================
-- 5. 看板模块
-- ===================================================

-- 看板表
CREATE TABLE IF NOT EXISTS kanban_kanbanboard (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('team', 'version', 'sub_project') DEFAULT 'team',
    project_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    INDEX idx_board_project (project_id)
) ENGINE=InnoDB;

-- 看板列表
CREATE TABLE IF NOT EXISTS kanban_kanbancolumn (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    `order` INT NOT NULL DEFAULT 0 COMMENT '排序序号',
    wip_limit INT DEFAULT 0 COMMENT '在制品限制, 0=无限制',
    board_id CHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (board_id) REFERENCES kanban_kanbanboard(id) ON DELETE CASCADE,
    INDEX idx_column_board (board_id),
    INDEX idx_column_order (board_id, `order`)
) ENGINE=InnoDB;

-- 任务与看板列的关联表
CREATE TABLE IF NOT EXISTS kanban_taskcolumn (
    id CHAR(36) PRIMARY KEY,
    task_id CHAR(36) NOT NULL,
    column_id CHAR(36) NOT NULL,
    `order` INT NOT NULL DEFAULT 0 COMMENT '在当前列中的排序',
    moved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_task_column (task_id, column_id),
    FOREIGN KEY (task_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    FOREIGN KEY (column_id) REFERENCES kanban_kanbancolumn(id) ON DELETE CASCADE,
    INDEX idx_tc_column (column_id)
) ENGINE=InnoDB;

-- ===================================================
-- 6. 工时与成本模块
-- ===================================================

-- 工时记录表
CREATE TABLE IF NOT EXISTS worklogs_worklog (
    id CHAR(36) PRIMARY KEY,
    task_id CHAR(36) NOT NULL,
    user_id CHAR(36) NOT NULL,
    hours DECIMAL(6,2) NOT NULL COMMENT '工时(小时)',
    date DATE NOT NULL COMMENT '工作日期',
    description TEXT COMMENT '工作内容',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    INDEX idx_worklog_task (task_id),
    INDEX idx_worklog_user (user_id),
    INDEX idx_worklog_date (date)
) ENGINE=InnoDB;

-- 工时费率表
CREATE TABLE IF NOT EXISTS worklogs_hourlyrate (
    id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    project_id CHAR(36) NOT NULL,
    rate DECIMAL(10,2) NOT NULL COMMENT '每小时费率(元)',
    effective_from DATE NOT NULL COMMENT '生效日期',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    UNIQUE KEY uk_user_project_rate (user_id, project_id, effective_from),
    INDEX idx_rate_user (user_id),
    INDEX idx_rate_project (project_id)
) ENGINE=InnoDB;

-- ===================================================
-- 7. 协作与评论模块
-- ===================================================

-- 评论表
CREATE TABLE IF NOT EXISTS tasks_comment (
    id CHAR(36) PRIMARY KEY,
    content TEXT NOT NULL,
    author_id CHAR(36) NOT NULL,
    task_id CHAR(36) DEFAULT NULL,
    project_id CHAR(36) DEFAULT NULL,
    parent_comment_id CHAR(36) DEFAULT NULL COMMENT '父评论ID, 用于嵌套回复',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_comment_id) REFERENCES tasks_comment(id) ON DELETE CASCADE,
    INDEX idx_comment_task (task_id),
    INDEX idx_comment_project (project_id),
    INDEX idx_comment_author (author_id)
) ENGINE=InnoDB;

-- @提及记录表 (从评论中提取)
CREATE TABLE IF NOT EXISTS tasks_mention (
    id CHAR(36) PRIMARY KEY,
    comment_id CHAR(36) NOT NULL,
    mentioned_user_id CHAR(36) NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (comment_id) REFERENCES tasks_comment(id) ON DELETE CASCADE,
    UNIQUE KEY uk_mention (comment_id, mentioned_user_id)
) ENGINE=InnoDB;

-- ===================================================
-- 8. 通知模块 → 由 Django migrations 管理（notifications_notification）
-- ===================================================

-- ===================================================
-- 9. 文件管理模块
-- ===================================================

CREATE TABLE IF NOT EXISTS files_attachment (
    id CHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '存储路径',
    file_size BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
    mime_type VARCHAR(100) DEFAULT 'application/octet-stream',
    task_id CHAR(36) DEFAULT NULL,
    project_id CHAR(36) DEFAULT NULL,
    uploader_id CHAR(36) NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks_task(id) ON DELETE CASCADE,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    INDEX idx_attach_task (task_id),
    INDEX idx_attach_project (project_id),
    INDEX idx_attach_uploader (uploader_id)
) ENGINE=InnoDB;

-- ===================================================
-- 10. 审计日志模块
-- ===================================================

CREATE TABLE IF NOT EXISTS core_activitylog (
    id CHAR(36) PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL COMMENT '实体类型: Task/Project/Sprint等',
    entity_id CHAR(36) NOT NULL COMMENT '实体ID',
    field_name VARCHAR(50) NOT NULL COMMENT '变更字段名',
    old_value TEXT COMMENT '旧值',
    new_value TEXT COMMENT '新值',
    changed_by CHAR(36) NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_activity_entity (entity_type, entity_id),
    INDEX idx_activity_changed_at (changed_at),
    INDEX idx_activity_changed_by (changed_by)
) ENGINE=InnoDB;

-- ===================================================
-- 11. 仪表盘模块
-- ===================================================

CREATE TABLE IF NOT EXISTS dashboards_dashboard (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    config JSON NOT NULL COMMENT '布局与小组件配置',
    user_id CHAR(36) NOT NULL,
    is_default TINYINT(1) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_dashboard_user (user_id)
) ENGINE=InnoDB;

-- ===================================================
-- 12. 报表模块 (可选扩展)
-- ===================================================

CREATE TABLE IF NOT EXISTS reports_report (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type ENUM('task_list', 'worklog_summary', 'gantt', 'progress', 'burndown') NOT NULL,
    project_id CHAR(36) NOT NULL,
    generated_by CHAR(36) NOT NULL,
    parameters JSON COMMENT '报表生成参数(时间范围/筛选条件)',
    file_path VARCHAR(500) COMMENT '导出文件路径',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects_project(id) ON DELETE CASCADE,
    INDEX idx_report_project (project_id)
) ENGINE=InnoDB;

-- ===================================================
-- 预设角色数据：由 Django 侧数据迁移 / 管理命令维护，勿在此 INSERT accounts_role
-- （否则在仅由 migrate 建表时会因无表或重复数据失败。）
-- ===================================================

-- ===================================================
-- 初始化默认看板列 (新建项目时可选模板)
-- ===================================================
-- 此处仅作参考, 实际列数据由应用层在创建看板时动态插入
-- 默认列: 待办(todo), 进行中(in_progress), 待审核(review), 已完成(done)
