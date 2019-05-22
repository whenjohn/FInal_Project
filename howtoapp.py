# howtoapp.py

from flask import request, redirect, url_for, Flask, render_template, session
import sqlite3 as lite
import time
import random

app = Flask(__name__)

app.secret_key = "my_secret_k3y'"

userid = 42


@app.route('/')
def index():
#    session.clear()
    return_howto_list_db = getHowtoListDB()
    return_howto_list_cookie = getHowToListCookie()

    if return_howto_list_cookie is None:
        session['howto'] = {}
        session.modified = True

    print session

    return render_template('index.html', howto_list_db=return_howto_list_db, howto_list_cookie=return_howto_list_cookie)


def getHowToListCookie():
    instr_array = session.get('howto')
    return instr_array


def getHowtoListDB():
    is_active = 1
    con = lite.connect('db_howto')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM tbl_howto WHERE active=? ORDER BY create_on DESC;", (is_active,))
    return cur.fetchall()

@app.route('/view')
def view():
    howto_id = request.args.get('hid')
    return_howto_instructions = getHowToInstructions(howto_id)
    return render_template('view.html', hid=howto_id, instructions=return_howto_instructions)


def getHowToInstructions(howto_id):
    con = lite.connect('db_howto')
    cur = con.cursor()
    cur.execute("SELECT * FROM tbl_instructions WHERE howto_id=? ORDER BY position ASC;", (howto_id,))
    return cur.fetchall()

    return render_template('view.html', h2id=howto_id)


@app.route('/instructions/<h2id>', methods=['GET', 'POST'])
def new_howto(h2id):
    if h2id == 'None':
        return_title = None
        return_instruction_intro = None
        return_instruction_list = None
        return_howto_id = None
    else:
        if 'title' in session['howto'][h2id].keys():
            return_title = session['howto'][h2id]['title']
        if 'intro' in session['howto'][h2id].keys():
            return_instruction_intro = session['howto'][h2id]['intro']
        if 'instructions' in session['howto'][h2id].keys():
            return_instruction_list = session['howto'][h2id]['instructions']
        return_howto_id = h2id


    if request.method == 'POST':
        if 'title' in request.form.keys() and request.form['title'] != "":
            return_howto_id = rando = random.randint(1,100001)
            session['howto'].update(
                {
                    int(return_howto_id) : {
                        'title' : request.form['title'],
                        'instructions' : {}
                    }
                }
            )
            session.modified = True
        else:
            return_howto_id = request.form['h2id']

            if 'intro' in request.form.keys() and request.form['intro'] != "":
                session['howto'][return_howto_id].update(
                    {
                        'intro': request.form['intro']
                    }
                )
                session.modified = True
                return_instruction_intro = session['howto'][return_howto_id]['intro']
            if 'step' in request.form.keys() and request.form['step'] != "":
                session['howto'][return_howto_id]['instructions'].update(
                    {
                        len(session['howto'][return_howto_id]['instructions']) + 1   : request.form['step']
                    }
                )
                session.modified = True
                return_instruction_list = session['howto'][return_howto_id]['instructions']

        return_title = session['howto'][return_howto_id]['title']


    else:
        if 'title' in session['howto'][h2id].keys():
            return_title = session['howto'][h2id]['title']
        if 'intro' in session['howto'][h2id].keys():
            return_instruction_intro = session['howto'][h2id]['intro']
        if 'instructions' in session['howto'][h2id].keys():
            return_instruction_list = session['howto'][h2id]['instructions']


    print session

    return render_template('instructions.html', h2id=return_howto_id, h2title=return_title, instruction_intro=return_instruction_intro, instruction_list=return_instruction_list)


@app.route('/publish/<h2id>')
def publish_howto(h2id):
#    print "publish", h2id
    datetime = time.time()
    instr_array = session['howto'][h2id]
    del session['howto'][h2id]
    session.modified = True
    new_howto = []
    new_instructions = []

    new_howto.extend([str(instr_array['title']), userid, datetime, None, True])

    con = lite.connect('db_howto')
    cur = con.cursor()
    cur.execute("INSERT INTO tbl_howto (title, author_id, create_on, edit_on, active) VALUES(?, ?, ?, ?, ?)", new_howto)
    con.commit()
    h2id_db = cur.lastrowid


    new_instructions.append((h2id_db, 0, str(instr_array['intro']), None))
    for key, value in instr_array['instructions'].iteritems():
        new_instructions.append((h2id_db, str(key), str(value), None))

    cur.executemany("INSERT INTO tbl_instructions (howto_id, position, in_body, edit_on) VALUES(?, ?, ?, ?)", new_instructions)
    con.commit()

    return redirect('/')


@app.route('/discard/<h2id>')
def delete_howto(h2id):
    del session['howto'][h2id]
    session.modified = True
    print session
    return redirect('/')


if __name__ == "__main__":
    app.run()
