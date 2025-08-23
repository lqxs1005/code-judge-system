-- 1. 用户表
CREATE TABLE `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `username` VARCHAR(64) NOT NULL COMMENT '用户名',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `email` VARCHAR(128) NOT NULL COMMENT '邮箱',
  `role` ENUM('admin', 'teacher', 'student') NOT NULL DEFAULT 'student' COMMENT '用户角色',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_username` (`username`),
  UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 2. 题目表
CREATE TABLE `problems` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `title` VARCHAR(255) NOT NULL COMMENT '题目标题',
  `description` TEXT NOT NULL COMMENT '题目描述',
  `type` ENUM('choice', 'fill_blank', 'short_answer', 'coding', 'code_snippet') NOT NULL COMMENT '题目类型',
  `difficulty` TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '难度等级（1-5）',
  `created_by` INT UNSIGNED NOT NULL COMMENT '创建者ID（外键，关联users.id）',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `language` ENUM('python', 'c', 'cpp') DEFAULT NULL COMMENT '编程题语言，仅编程题有效',
  `reference_code` TEXT DEFAULT NULL COMMENT '参考代码，仅编程题有效',
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `fk_problems_created_by` FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='题目表';

-- 3. 测试用例表
CREATE TABLE `test_cases` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `problem_id` INT UNSIGNED NOT NULL COMMENT '题目ID（外键）',
  `input_data` TEXT NOT NULL COMMENT '输入数据',
  `expected_output` TEXT NOT NULL COMMENT '期望输出',
  `is_hidden` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否为隐藏用例',
  PRIMARY KEY (`id`),
  KEY `idx_problem_id` (`problem_id`),
  CONSTRAINT `fk_test_cases_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `problems`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例表';

-- 4. 作业表
CREATE TABLE `assignments` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `title` VARCHAR(255) NOT NULL COMMENT '作业标题',
  `description` TEXT COMMENT '作业描述',
  `start_time` DATETIME NOT NULL COMMENT '开始时间',
  `end_time` DATETIME NOT NULL COMMENT '结束时间',
  `created_by` INT UNSIGNED NOT NULL COMMENT '创建者ID（老师，外键）',
  PRIMARY KEY (`id`),
  KEY `idx_created_by` (`created_by`),
  CONSTRAINT `fk_assignments_created_by` FOREIGN KEY (`created_by`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业表';

-- 5. 作业-题目关系表
CREATE TABLE `assignment_problems` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `assignment_id` INT UNSIGNED NOT NULL COMMENT '作业ID（外键）',
  `problem_id` INT UNSIGNED NOT NULL COMMENT '题目ID（外键）',
  `score` DECIMAL(5,2) NOT NULL DEFAULT 0 COMMENT '题目分值',
  PRIMARY KEY (`id`),
  KEY `idx_assignment_id` (`assignment_id`),
  KEY `idx_problem_id` (`problem_id`),
  CONSTRAINT `fk_assignment_problems_assignment_id` FOREIGN KEY (`assignment_id`) REFERENCES `assignments`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_assignment_problems_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `problems`(`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作业-题目关系表';

-- 6. 提交记录表
CREATE TABLE `submissions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `user_id` INT UNSIGNED NOT NULL COMMENT '用户ID（外键）',
  `problem_id` INT UNSIGNED NOT NULL COMMENT '题目ID（外键）',
  `assignment_id` INT UNSIGNED DEFAULT NULL COMMENT '作业ID（外键，可为空）',
  `code` TEXT NOT NULL COMMENT '用户提交的代码（需加密存储）',
  `language` ENUM('python', 'c', 'cpp') NOT NULL COMMENT '代码语言',
  `status` ENUM('judging', 'accepted', 'wrong_answer', 'runtime_error', 'compile_error', 'time_limit_exceeded', 'memory_limit_exceeded', 'output_limit_exceeded', 'system_error') NOT NULL DEFAULT 'judging' COMMENT '评测状态',
  `result` JSON DEFAULT NULL COMMENT '评测结果（JSON格式）',
  `submitted_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '提交时间',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_problem_id` (`problem_id`),
  KEY `idx_assignment_id` (`assignment_id`),
  CONSTRAINT `fk_submissions_user_id` FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_submissions_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `problems`(`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_submissions_assignment_id` FOREIGN KEY (`assignment_id`) REFERENCES `assignments`(`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提交记录表';
