
#!/usr/bin/env python
import os

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from application import creat_app
from flask_script import Manager, Shell, Server

app = creat_app()
manager = Manager(app)

def make_shell_context():
    return dict(app=app)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", Server(host='0.0.0.0',port=5000,))
@manager.command
def deploy():
    """Run deployment tasks."""
    pass


if __name__ == "__main__":
    manager.run()
