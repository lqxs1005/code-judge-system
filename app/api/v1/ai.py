from flask import Blueprint, request, jsonify, g, current_app
from app.utils import token_required
from app.models import User
from app.extensions import db
import openai
import json

def build_prompt(problem_type, params):
    if problem_type == 'choice':
        return f'''
你是一名专业的出题专家。请根据以下要求生成一道选择题，并严格只返回一个JSON对象，不包含任何解释或Markdown代码块。
{{
  "title": "题目标题",
  "description": "题目描述",
  "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
  "answer": "A",
  "explanation": "答案解析"
}}
要求：
- 主题：{params.get('topic')}
- 难度：{params.get('difficulty')}
- 题型：选择题
- 题目描述清晰，选项合理，答案唯一，解析详细。
'''
    elif problem_type == 'fill_blank':
        return f'''
你是一名专业的出题专家。请根据以下要求生成一道填空题，并严格只返回一个JSON对象，不包含任何解释或Markdown代码块。
{{
  "title": "题目标题",
  "description": "题目描述，包含空格位置说明",
  "answers": ["正确答案1", "正确答案2"],
  "explanation": "答案解析"
}}
要求：
- 主题：{params.get('topic')}
- 难度：{params.get('difficulty')}
- 题型：填空题
- 题目描述清晰，答案唯一或有多个正确答案，解析详细。
'''
    elif problem_type == 'short_answer':
        return f'''
你是一名专业的出题专家。请根据以下要求生成一道简答题，并严格只返回一个JSON对象，不包含任何解释或Markdown代码块。
{{
  "title": "题目标题",
  "description": "题目描述",
  "key_points": ["关键点1", "关键点2"],
  "scoring_criteria": ["评分准则1", "评分准则2"]
}}
要求：
- 主题：{params.get('topic')}
- 难度：{params.get('difficulty')}
- 题型：简答题
- 题目描述清晰，给出关键点和评分准则，便于后续AI自动评分。
'''
    elif problem_type == 'code_snippet':
        return f'''
你是一名专业的编程题出题专家。请根据以下要求生成一道片段编程题，并严格只返回一个JSON对象，不包含任何解释或Markdown代码块。
{{
  "title": "题目标题",
  "description": "题目描述，说明需要补全的部分",
  "code_snippet": "给出的代码片段（含空缺）",
  "expected_completion": "正确补全内容",
  "example_input": "示例输入",
  "example_output": "示例输出",
  "test_cases": [
    {{"input": "...", "expected_output": "..."}},
    ...
  ],
  "reference_code": "完整正确代码"
}}
要求：
- 主题：{params.get('topic')}
- 难度：{params.get('difficulty')}
- 题型：片段编程题
- 题目描述清晰，代码片段有明确空缺，补全内容唯一，测试用例全面。
'''
    else:
        # 默认回退到编程题
        return f'''
你是一名专业的编程题目出题专家。请根据以下要求，严格生成一道高质量的编程题，并只返回一个JSON对象，不包含任何解释、说明、Markdown代码块或多余内容。
{{
  "title": "字符串，题目标题",
  "description": "字符串，题目详细描述，包含需求和约束",
  "example_input": "字符串，示例输入",
  "example_output": "字符串，示例输出",
  "test_cases": [
    {{"input": "字符串，测试用例输入", "expected_output": "字符串，期望输出"}},
    ...
  ],
  "reference_code": "字符串，参考代码"
}}
要求：
- 主题：{params.get('topic')}
- 难度：{params.get('difficulty')}
- 题型：编程题
- 题目描述清晰，测试用例全面，参考代码规范。
'''

def build_short_answer_scoring_prompt(question, key_points, scoring_criteria, student_answer):
    return f"""
你是一名专业的自动阅卷专家。请根据以下简答题的题干、关键点、评分准则，对学生的答案进行评分，并只返回一个JSON对象，不包含任何解释或Markdown代码块。

题目描述：{question}
关键点：{key_points}
评分准则：{scoring_criteria}
学生答案：{student_answer}

请严格按照如下JSON结构返回：
{{
  "score": 0-100,  // 整数分数
  "comment": "简要评语，指出优点和不足"
}}

评分要求：
- 依据关键点和评分准则，逐条判断学生答案是否覆盖要点。
- 分数为0-100的整数，评语简明扼要。
"""

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/ai/generate-problem', methods=['POST'])
@token_required
def generate_problem():
    user_id = getattr(g, 'current_user_id', None)
    user = db.session.get(User, user_id)
    if not user or user.role not in ('teacher', 'admin'):
        return jsonify({'msg': 'Only teacher or admin can use this feature'}), 403

    data = request.get_json()
    topic = data.get('topic')
    difficulty = data.get('difficulty')
    type_ = data.get('type')
    language = data.get('language')

    if not topic or not difficulty or not type_:
        return jsonify({'msg': 'Missing required parameters'}), 400

    prompt = build_prompt(type_, {
        'topic': topic,
        'difficulty': difficulty,
        'language': language or ''
    })

    try:
        openai.api_key = current_app.config['OPENAI_API_KEY']
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一名专业的题目出题专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        content = response.choices[0].message['content']
        try:
            problem_json = json.loads(content)
        except Exception as e:
            return jsonify({'msg': 'AI返回内容无法解析为JSON', 'raw': content, 'error': str(e)}), 500
        return jsonify({'problem': problem_json}), 200
    except Exception as e:
        return jsonify({'msg': 'AI generation failed', 'detail': str(e)}), 500

@ai_bp.route('/ai/score-short-answer', methods=['POST'])
@token_required
def score_short_answer():
    data = request.get_json()
    question = data.get('question')
    key_points = data.get('key_points')
    scoring_criteria = data.get('scoring_criteria')
    student_answer = data.get('student_answer')

    if not all([question, key_points, scoring_criteria, student_answer]):
        return jsonify({'msg': 'Missing required fields'}), 400

    prompt = build_short_answer_scoring_prompt(
        question, key_points, scoring_criteria, student_answer
    )

    try:
        openai.api_key = current_app.config['OPENAI_API_KEY']
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一名专业的自动阅卷专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=256
        )
        content = response.choices[0].message['content']
        try:
            score_json = json.loads(content)
        except Exception as e:
            return jsonify({'msg': 'AI返回内容无法解析为JSON', 'raw': content, 'error': str(e)}), 500
        return jsonify({'score': score_json.get('score'), 'comment': score_json.get('comment')}), 200
    except Exception as e:
        return jsonify({'msg': 'AI评分失败', 'detail': str(e)}), 500
