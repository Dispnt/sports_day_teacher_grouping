from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/TeacherSports'
db = SQLAlchemy(app)

class VotingRecords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(255), nullable=False)
    team = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)

class TeacherProjects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(255), nullable=False)
    project_name = db.Column(db.String(255), nullable=False)
    team = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)

# 映射英文项目名称到中文
english_to_chinese_map = {
    'Solid Ball': '实心球',
    'Basketball': '篮球',
    'Badminton': '羽毛球',
    'Jump Rope': '跳绳',
    'Blue': '蓝',
    'Red': '红'
    # 添加其他项目的映射
}

# 根据英文项目名称返回中文名称的方法
def translate_to_chinese(english_name):
    return english_to_chinese_map.get(english_name, english_name) 


# 首页路由，渲染投票页面
@app.route('/')
def index():
    return render_template('eventvote.html')

# 投票接口路由
@app.route('/vote', methods=['POST'])
def vote():
    try:
        data = request.json  # 获取JSON数据
        name = data.get('name')
        team = data.get('team')

        existing_vote = VotingRecords.query.filter_by(teacher_name=name).first()
        if name and team:
            if existing_vote: # 如果存在
                # 检查队伍是否已满
                team_size = VotingRecords.query.filter_by(team=team).count()
                if team_size >= 40:
                    return 402
                existing_vote.team = team
                db.session.commit()
                return jsonify({'selectorupdate': '更新了队伍，现在是'})
            else: # 如果不存在
                # 检查队伍是否已满
                team_size = VotingRecords.query.filter_by(team=team).count()
                if team_size >= 40:
                    return 402
                new_vote = VotingRecords(teacher_name=name, team=team)
                db.session.add(new_vote)
                db.session.commit()
                return jsonify({'selectorupdate': '选择了'})
        else:
            return 401
    except Exception as e:
        print(e)
        return 400

# 获取投票进度接口路由
@app.route('/vote/status', methods=['GET'])
def get_vote_status():
    try:
        # 查询数据库，获取投票进度
        blue_votes = VotingRecords.query.filter_by(team='blue').count()
        red_votes = VotingRecords.query.filter_by(team='red').count()

        return jsonify({'blue': blue_votes, 'red': red_votes})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/vote/project', methods=['POST'])
def vote_project():
    try:
        data = request.json
        name = data.get('name')
        project = data.get('project')
        team = data.get('team')

        # Check if the teacher has already signed up for this project
        existing_vote = TeacherProjects.query.filter_by(teacher_name=name, project_name=project, team=team).first()

        if existing_vote:
            # If the teacher has already signed up, cancel the registration
            db.session.delete(existing_vote)
            db.session.commit()
            return jsonify({'success': True, 'message': f'取消报名 {translate_to_chinese(project)} 项目成功！'})

        # Check if the teacher can participate in the project
        if TeacherProjects.query.filter_by(teacher_name=name, team=team).count() >= 3:
            return jsonify({'success': False, 'message': '您最多可以选择三个项目。'})

        # Check if the team is full
        team_size = TeacherProjects.query.filter_by(team=team, project_name=project).count()
        if team_size >= 5:
            return jsonify({'success': False, 'message': f'{translate_to_chinese(team)}队的 {translate_to_chinese(project)} 项目已满，不能再选。'})

        # Insert a new record
        new_vote_project = TeacherProjects(teacher_name=name, project_name=project, team=team)
        db.session.add(new_vote_project)
        db.session.commit()

        return jsonify({'success': True, 'message': '选择项目成功！'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/project/team/count', methods=['GET'])
def get_project_team_count():
    try:
        project = request.args.get('project')
        team = request.args.get('team')

        count = TeacherProjects.query.filter_by(project_name=project, team=team).count()

        return jsonify({'success': True, 'count': count})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})



@app.route('/project/enrolled', methods=['GET'])
def get_enrolled_projects():
    try:
        name = request.args.get('name')  # 通过查询参数获取教工姓名
        team = request.args.get('team')  # 通过查询参数获取队伍名称
        print(f'{name}进行了查询请求')
        # 查询当前报名了哪些项目
        enrolled_projects = TeacherProjects.query.filter_by(teacher_name=name, team=team).all()
        # 构造项目列表
        projects_list = [{'project': project.project_name, 'timestamp': project.timestamp} for project in enrolled_projects]

        return jsonify({'success': True, 'projects': projects_list})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# @app.route('/project/status', methods=['GET'])
# def index():
#     teacher_projects = TeacherProjects.query.all()
#     return jsonify({'success': True, 'projects': teacher_projects})

if __name__ == '__main__':
    serve(app, listen='*:80')
    # app.run(host='0.0.0.0',port=80,debug=True)
