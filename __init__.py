import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'resortmanagementsystem.sqlite'),
    )

    from ResortManagementSystem import adm, auth, db, resort, emp, guest

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_pyfile(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(adm.bp)
    app.register_blueprint(resort.bp)
    app.register_blueprint(emp.bp)
    app.register_blueprint(guest.bp)

    return app
