# coding=utf-8
import os
import time
import hashlib
import flask as f
import sqlalchemy as db
import flask_bootstrap as fb


commands = []
commands.append('df -h')
commands.append('free -g')
commands.append('uname -a')
commands.append('ps -ef')
commands.append('cat /proc/cpuinfo')
commands.append('mount')
commands.append('netstat -tlnp')
commands.append('iptables -nL')
engine = db.create_engine('sqlite:///database.sqlite')
app = f.Flask('py_vulnerable_site')
fb.Bootstrap(app)


def query(text):
    conn = engine.connect()
    res = conn.execute(text)
    res = res.fetchall()
    return res


def execsql(text):
    conn = engine.connect()
    return conn.execute(text)


def hash(text):
    hashed = hashlib.md5(text.encode('utf-8'))
    return hashed.hexdigest()


@app.route('/', methods=['GET'])
def get_index():
    posts = f'SELECT * FROM posts;'
    posts = query(posts)
    return f.render_template('index.html', items=posts)


@app.route('/about', methods=['GET'])
def get_about():
    files = os.listdir('./static/legal/')
    files = list(map(lambda i: i.split('.')[0], files))
    doc = f.request.args.get('doc')
    if doc:
        url = './static/legal/' + doc + '.txt'
        doc = os.popen(f'cat {url}').read()
    else:
        doc = 'Selecione um documento para ler nos links acima.'
    return f.render_template('about.html', files=files, doc=doc)


@app.route('/contact', methods=['GET'])
def get_contact():
    messages = f'SELECT * FROM book ORDER BY sign_date DESC;'
    res = query(messages)
    return f.render_template('contact.html', items=res)


@app.route('/contact', methods=['POST'])
def post_contact():
    cookie = f.request.cookies.get('pyverysafelogin')
    if cookie:
        n = time.strftime('%Y%m%d%H%M%S', time.gmtime())
        name = f.request.form['name']
        message = f.request.form['message']
        sql = f'''
        INSERT INTO book(sign_date, name, message)
        VALUES('{n}', '{name}', '{message}');
        '''
        execsql(sql)
        redirect = f.redirect('/contact#Livro')
        r = f.make_response(redirect)
        return r
    else:
        return f.render_template('/login.html',
                                 msg='Faça login para assinar o livro.')


@app.route('/signup', methods=['GET'])
def get_signup():
    return f.render_template('signup.html')


@app.route('/signup', methods=['POST'])
def post_signup():
    name = f.request.form['name']
    login = f.request.form['login']
    email = f.request.form['email']
    password = f.request.form['senha']
    photo = f.request.files['photo']
    extension = photo.filename.split('.')[-1]
    pname = hash(login) + '.' + extension
    photo.save('./static/uploads/' + pname)
    sql = f'''
    SELECT login
    FROM logins
    WHERE login = '{hash(login)}';
    '''
    if len(query(sql)) == 0:
        sql = f'''
        INSERT INTO logins (name, picture, login, email, type, password)
        VALUES ('{name}', '{pname}', '{hash(login)}',
                '{email}', 'user', '{hash(password)}');
        '''
        execsql(sql)
        msg = f'Usuário criado, {name}!'
    else:
        sql = f'''
        UPDATE logins
        SET
            name = '{name}',
            picture = '{pname}',
            email = '{email}',
            type = 'user',
            password = '{hash(password)}'
        WHERE login = '{hash(login)}';
        '''
        execsql(sql)
        msg = f'Usuário atualizado, {name}!'
    return f.render_template('signup.html', msg=msg)


@app.route('/login', methods=['GET'])
def get_login():
    return f.render_template('/login.html', msg='')


@app.route('/login', methods=['POST'])
def post_login():
    lg = hash(f.request.form['login'] or 'blank')
    pw = hash(f.request.form['senha'] or 'blank')
    q = f'''
    SELECT type
    FROM logins
    WHERE login = "{lg}"
    AND password = "{pw}"
    '''
    res = query(q)
    if len(res) == 0:
        return f.render_template('/login.html', msg='Login incorreto!')
    else:
        res = res[0][0]
        redirect = f.redirect('/restrict')
        r = f.make_response(redirect)
        r.set_cookie('pyverysafelogin', value=hash(res))
        r.set_cookie('pyverysafeid', value=lg)
        return r


@app.route('/restrict', methods=['GET'])
def get_restrict():
    cookie = f.request.cookies.get('pyverysafelogin')
    if cookie:
        q = f'SELECT info FROM info WHERE level LIKE "%{cookie}%"'
        res = query(q)
        if cookie == hash('admin'):
            lv = 'Admin'
        else:
            lv = 'Comum'
        return f.render_template('restrict.html', level=lv, info=res)
    else:
        return f.render_template('/login.html',
                                 msg='Faça login para ver as profecias.')


@app.route('/profile', methods=['GET'])
def get_profile():
    cookie = f.request.cookies.get('pyverysafeid')
    if cookie:
        sql = f'''
        SELECT picture, name, email, type
        FROM logins
        WHERE login = '{cookie}';
        '''
        res = query(sql)
        if len(res) > 0:
            res = res[0]
        print(str(res))
        return f.render_template('profile.html',
                                 foto='/static/uploads/'+res[0],
                                 nome=res[1],
                                 email=res[2],
                                 grupo=res[3])
    else:
        return f.render_template('/login.html', msg='Faça login primeiro.')


@app.route('/logout', methods=['GET'])
def get_logout():
    redirect = f.redirect('/login')
    r = f.make_response(redirect)
    r.set_cookie('pyverysafelogin', '', expires=0)
    r.set_cookie('pyverysafeid', '', expires=0)
    return r


@app.route('/search', methods=['GET'])
def get_search():
    search = f.request.args.get('text')
    search = f'SELECT * FROM posts WHERE Content LIKE "%{search}%";'
    res = query(search)
    if len(res) == 0:
        res = [('Que Pena!', 'Sua pesquisa não retornou resultados. \
                Tenta outra coisa :D')]
    return f.render_template('search.html', items=res)


@app.route('/status', methods=['GET'])
def get_status():
    return f.render_template('status.html', commands=commands)


@app.route('/status', methods=['POST'])
def post_status():
    cookie = f.request.cookies.get('pyverysafelogin')
    if cookie == hash('admin'):
        cmd = f.request.form['cmd']
        r = os.popen(cmd).read()
        return f.render_template('status.html', commands=commands, results=r)
    else:
        return f.redirect('/login')


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=8000)
