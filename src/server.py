import os
from flask import Flask, render_template
from .generate_html import generate_render_data


app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'templates'), static_folder=os.path.join(os.getcwd(), 'static'))


@app.route('/', methods=['GET'])
def index():
    render_data = generate_render_data()
    return render_template('holodule.html', **render_data)


if __name__ == "__main__":
    app.run()
