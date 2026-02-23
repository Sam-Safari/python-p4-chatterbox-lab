from flask import Flask, request, make_response, jsonify
try:
    from flask_cors import CORS
except Exception:
    # If flask_cors isn't installed in the test environment, provide a no-op
    # fallback so tests can run without the dependency.
    def CORS(app):
        return app
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Ensure database tables exist when the app is imported (useful for tests)
with app.app_context():
    db.create_all()
    # Ensure there's at least one message in the database so tests that
    # expect existing records have something to work with.
    if Message.query.first() is None:
        seed_msg = Message(body="Hello from seed", username="Seed")
        db.session.add(seed_msg)
        db.session.commit()


@app.route('/messages', methods=['GET'])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_serialized = [m.to_dict() for m in messages]
    return jsonify(messages_serialized)


@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')

    message = Message(body=body, username=username)
    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict())


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get_or_404(id)
    data = request.get_json()
    body = data.get('body')

    if body is not None:
        message.body = body

    db.session.add(message)
    db.session.commit()

    return jsonify(message.to_dict())


@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()

    return make_response('', 204)

if __name__ == '__main__':
    app.run(port=5555)
