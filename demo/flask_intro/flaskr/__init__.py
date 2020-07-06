import os
from flask import Flask, jsonify




app.config.from_mapping(
 SECRET_KEY='dev',
 DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
 )


@app.route('/')
def hello_world():
    return 'Hello, World!'

return app