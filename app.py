import flask, os, json
from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

from bot import get_time

app = flask.Flask(__name__)

class InfoForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    idnum = StringField('学号', validators=[DataRequired()])
    url = StringField('抢讲座链接', validators=[DataRequired()])
    submit = SubmitField('提交')



@app.route('/', methods=['POST', 'GET'])
def index():
    back_log = os.path.join('back_log', 'back.json')

    if request.method == 'POST':
        try:
            form = request.form
            data = form.to_dict()
            data.pop('submit')
            data['time'] = get_time(data['url'])
            data['status'] = 'waiting'
            
            with open(back_log) as f:
                origin = json.load(f)
            origin.append(data)
            with open(back_log, 'w') as f:
                json.dump(origin, f)
        except:
            print('Parsing data failed.')
        
        if data['time'] != None:
            os.system('python3 bot.py --url %s --name %s --id %s &' % (data['url'], data['name'], data['idnum']))

    with open(back_log) as f:
        infos = json.load(f)

    form = InfoForm(meta={'csrf': False})
    return flask.render_template('index.html', form=form, infos=infos)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port= 5000, debug=False)
