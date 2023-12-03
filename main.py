from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/TeacherSports'
db = SQLAlchemy(app)

class VotingRecords(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_name = db.Column(db.String(255), nullable=False)
    team = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.now(), nullable=False)

# 首页路由，渲染投票页面
@app.route('/')
def index():
    return render_template('index.html')

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
                if team_size >= 5:
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

if __name__ == '__main__':
    app.run(debug=True)
