"""Run an isolated, localhost-only client demo with fictional leads."""

from argparse import ArgumentParser
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from app import create_app
from app.models import Lead, Program, TrainingType, User, db
from config import Config


class DemoConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///gym_demo.db'
    SECRET_KEY = token_urlsafe(32)


def prepare_demo(app):
    with app.app_context():
        admin = User.query.filter_by(username='demo').first()
        if admin is not None:
            return

        password = token_urlsafe(12)
        admin = User(username='demo', email='staff@example.test')
        admin.set_password(password)
        db.session.add(admin)

        programs = Program.query.order_by(Program.order_num).all()
        formats = TrainingType.query.order_by(TrainingType.order_num).all()
        stages = (
            'New', 'Contacted', 'Trial Done', 'Converted',
            'New', 'Contacted', 'Converted', 'Not Interested',
        )
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        for index, stage in enumerate(stages):
            sequence = index + 1
            db.session.add(Lead(
                name=f'Sample Member {sequence:02}',
                phone=f'{sequence:010}',
                email=f'member{sequence}@example.test',
                gender='Male' if index % 2 == 0 else 'Female',
                fitness_goal=programs[index % len(programs)].title,
                training_type=formats[index % len(formats)].title,
                status=stage,
                created_at=now - timedelta(hours=index * 11),
            ))

        db.session.commit()
        print(f'Demo login: demo / {password}', flush=True)
        print('Save this password for future runs of this demo database.', flush=True)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    app = create_app(DemoConfig)
    prepare_demo(app)
    print(f'Public site: http://127.0.0.1:{args.port}/', flush=True)
    print(f'Staff portal: http://127.0.0.1:{args.port}/admin/login', flush=True)
    app.run(host='127.0.0.1', port=args.port, debug=False)
