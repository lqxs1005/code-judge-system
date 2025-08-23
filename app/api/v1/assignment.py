from flask import Blueprint, request, jsonify, g
from app.extensions import db
from app.models import Assignment, AssignmentProblem, Problem, User
from app.schemas import AssignmentSchema, ProblemSchema
from app.utils import token_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

assignment_bp = Blueprint('assignment', __name__)

def is_teacher_or_admin(user):
    return user and user.role in ('teacher', 'admin')

def get_current_user():
    user_id = getattr(g, 'current_user_id', None)
    if not user_id:
        return None
    return db.session.get(User, user_id)

@assignment_bp.route('/assignments', methods=['POST'])
@token_required
def create_assignment():
    user = get_current_user()
    if not is_teacher_or_admin(user):
        return jsonify({'msg': 'Only teacher or admin can create assignments'}), 403

    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    start_time = data.get('start_time')
    end_time = data.get('end_time')

    if not title or not start_time or not end_time:
        return jsonify({'msg': 'title, start_time, end_time are required'}), 400

    try:
        assignment = Assignment(
            title=title,
            description=description,
            start_time=datetime.fromisoformat(start_time),
            end_time=datetime.fromisoformat(end_time),
            created_by=user.id
        )
        db.session.add(assignment)
        db.session.commit()
        return jsonify({
            'msg': 'Assignment created',
            'assignment': AssignmentSchema().dump(assignment)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to create assignment', 'detail': str(e)}), 500

@assignment_bp.route('/assignments/<int:assignment_id>/problems', methods=['POST'])
@token_required
def add_problems_to_assignment(assignment_id):
    user = get_current_user()
    if not is_teacher_or_admin(user):
        return jsonify({'msg': 'Only teacher or admin can add problems'}), 403

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'msg': 'Assignment not found'}), 404
    if assignment.created_by != user.id and user.role != 'admin':
        return jsonify({'msg': 'No permission to modify this assignment'}), 403

    data = request.get_json()
    problems = data if isinstance(data, list) else data.get('problems')
    if not problems or not isinstance(problems, list):
        return jsonify({'msg': 'A list of problems is required'}), 400

    problem_ids = [item.get('problem_id') for item in problems]
    if not all(isinstance(pid, int) for pid in problem_ids):
        return jsonify({'msg': 'Each problem_id must be an integer'}), 400
    found_problems = Problem.query.filter(Problem.id.in_(problem_ids)).all()
    found_ids = {p.id for p in found_problems}
    not_found = [pid for pid in problem_ids if pid not in found_ids]
    if not_found:
        return jsonify({'msg': f'Problems not found: {not_found}'}), 404

    try:
        added = []
        with db.session.begin_nested():
            for item in problems:
                pid = item['problem_id']
                score = item.get('score', 0)
                exists = AssignmentProblem.query.filter_by(assignment_id=assignment_id, problem_id=pid).first()
                if exists:
                    continue
                ap = AssignmentProblem(assignment_id=assignment_id, problem_id=pid, score=score)
                db.session.add(ap)
                added.append({'problem_id': pid, 'score': score})
        db.session.commit()
        return jsonify({
            'msg': 'Problems added to assignment',
            'count': len(added),
            'added': added
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'msg': 'Failed to add problems', 'detail': str(e)}), 500

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@token_required
def get_assignment_detail(assignment_id):
    user = get_current_user()
    if not is_teacher_or_admin(user):
        return jsonify({'msg': 'Only teacher or admin can view assignments'}), 403

    assignment = Assignment.query.get(assignment_id)
    if not assignment:
        return jsonify({'msg': 'Assignment not found'}), 404
    if assignment.created_by != user.id and user.role != 'admin':
        return jsonify({'msg': 'No permission to view this assignment'}), 403

    problems = AssignmentProblem.query.filter_by(assignment_id=assignment_id).all()
    problem_list = []
    for ap in problems:
        problem = Problem.query.get(ap.problem_id)
        if problem:
            p = ProblemSchema().dump(problem)
            p['score'] = ap.score
            problem_list.append(p)

    return jsonify({
        'assignment': AssignmentSchema().dump(assignment),
        'problems': problem_list
    }), 200

@assignment_bp.route('/ai/generate-assignment', methods=['POST'])
@token_required
def generate_assignment_auto():
    user = get_current_user()
    if not is_teacher_or_admin(user):
        return jsonify({'msg': 'Only teacher or admin can use this feature'}), 403

    data = request.get_json()
    topic = data.get('topic')
    difficulty = data.get('difficulty')
    problem_count = data.get('problem_count')
    type_distribution = data.get('type_distribution')

    if not topic or not difficulty or not problem_count:
        return jsonify({'msg': 'topic, difficulty, problem_count are required'}), 400

    return jsonify({
        'msg': '自动组卷逻辑待实现',
        'received': {
            'topic': topic,
            'difficulty': difficulty,
            'problem_count': problem_count,
            'type_distribution': type_distribution
        }
    }), 200
