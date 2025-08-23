from .extensions import db
from sqlalchemy.dialects.mysql import ENUM, TINYINT, INTEGER, DATETIME, DECIMAL, JSON
from sqlalchemy import text

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = db.Column(db.String(64), unique=True, nullable=False, comment='用户名')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    email = db.Column(db.String(128), unique=True, nullable=False, comment='邮箱')
    role = db.Column(ENUM('admin', 'teacher', 'student'), nullable=False, default='student', comment='用户角色')
    created_at = db.Column(DATETIME(fsp=0), nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    # 反向引用
    problems = db.relationship('Problem', backref='creator', lazy='dynamic', foreign_keys='Problem.created_by')
    assignments = db.relationship('Assignment', backref='creator', lazy='dynamic', foreign_keys='Assignment.created_by')
    submissions = db.relationship('Submission', backref='user', lazy='dynamic', foreign_keys='Submission.user_id')

    def __repr__(self):
        return f'<User {self.username}>'

class Problem(db.Model):
    __tablename__ = 'problems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    title = db.Column(db.String(255), nullable=False, comment='题目标题')
    description = db.Column(db.Text, nullable=False, comment='题目描述')
    type = db.Column(ENUM('choice', 'fill_blank', 'short_answer', 'coding', 'code_snippet'), nullable=False, comment='题目类型')
    difficulty = db.Column(TINYINT(unsigned=True), nullable=False, default=1, comment='难度等级（1-5）')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='创建者ID（外键，关联users.id）')
    created_at = db.Column(DATETIME(fsp=0), nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')
    language = db.Column(ENUM('python', 'c', 'cpp'), nullable=True, comment='编程题语言，仅编程题有效')
    reference_code = db.Column(db.Text, nullable=True, comment='参考代码，仅编程题有效')

    # 反向引用
    test_cases = db.relationship('TestCase', backref='problem', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='TestCase.problem_id')
    assignment_problems = db.relationship('AssignmentProblem', backref='problem', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='AssignmentProblem.problem_id')
    submissions = db.relationship('Submission', backref='problem', lazy='dynamic', foreign_keys='Submission.problem_id')

    def __repr__(self):
        return f'<Problem {self.title}>'

class TestCase(db.Model):
    __tablename__ = 'test_cases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='题目ID（外键）')
    input_data = db.Column(db.Text, nullable=False, comment='输入数据')
    expected_output = db.Column(db.Text, nullable=False, comment='期望输出')
    is_hidden = db.Column(TINYINT(1), nullable=False, default=0, comment='是否为隐藏用例')

    def __repr__(self):
        return f'<TestCase {self.id} for Problem {self.problem_id}>'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    title = db.Column(db.String(255), nullable=False, comment='作业标题')
    description = db.Column(db.Text, comment='作业描述')
    start_time = db.Column(DATETIME(fsp=0), nullable=False, comment='开始时间')
    end_time = db.Column(DATETIME(fsp=0), nullable=False, comment='结束时间')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='创建者ID（老师，外键）')

    # 反向引用
    assignment_problems = db.relationship('AssignmentProblem', backref='assignment', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='AssignmentProblem.assignment_id')
    submissions = db.relationship('Submission', backref='assignment', lazy='dynamic', foreign_keys='Submission.assignment_id')

    def __repr__(self):
        return f'<Assignment {self.title}>'

class AssignmentProblem(db.Model):
    __tablename__ = 'assignment_problems'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='作业ID（外键）')
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='题目ID（外键）')
    score = db.Column(DECIMAL(5,2), nullable=False, default=0, comment='题目分值')

    def __repr__(self):
        return f'<AssignmentProblem Assignment {self.assignment_id} Problem {self.problem_id}>'

class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='用户ID（外键）')
    problem_id = db.Column(db.Integer, db.ForeignKey('problems.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True, comment='题目ID（外键）')
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id', ondelete='SET NULL', onupdate='CASCADE'), nullable=True, index=True, comment='作业ID（外键，可为空）')
    code = db.Column(db.Text, nullable=False, comment='用户提交的代码（需加密存储）')
    language = db.Column(ENUM('python', 'c', 'cpp'), nullable=False, comment='代码语言')
    status = db.Column(ENUM('judging', 'accepted', 'wrong_answer', 'runtime_error', 'compile_error', 'time_limit_exceeded', 'memory_limit_exceeded', 'output_limit_exceeded', 'system_error'), nullable=False, default='judging', comment='评测状态')
    result = db.Column(JSON, nullable=True, comment='评测结果（JSON格式）')
    submitted_at = db.Column(DATETIME(fsp=0), nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='提交时间')

    def __repr__(self):
        return f'<Submission {self.id} by User {self.user_id}>'
