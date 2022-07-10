from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import APP
from models import db

migrate = Migrate(APP, db)
manager = Manager(APP)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()