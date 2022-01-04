from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)








@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = data.get('user')
    password = data.get('password')


    return redirect(url_for('index'))



@app.route('/index')
def index():
    return render_template('index.html')


host_addr = "0.0.0.0"
port_num = "8080"
if __name__ == "__main__":
    app.run(host_addr, port_num)