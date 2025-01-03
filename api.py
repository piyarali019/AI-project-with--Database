from flask_restful import Resource, reqparse, Api, marshal
from flask_restful import fields
from models import db, User, Card, Deck, app
from flask_security import auth_required

api = Api(app)

# Request Parsers
create_user_parser = reqparse.RequestParser()
create_user_parser.add_argument('username')
create_user_parser.add_argument('password')

update_deck_parser = reqparse.RequestParser()
update_deck_parser.add_argument('deck_new')
update_deck_parser.add_argument('deck_value')

update_card_parser = reqparse.RequestParser()
update_card_parser.add_argument('card_new')
update_card_parser.add_argument('card_value')

create_card_parser = reqparse.RequestParser()
create_card_parser.add_argument('card_name')
create_card_parser.add_argument('card_value')

# Response Fields
card_resource_fields = {
    'card_id': fields.Integer,
    'card_name': fields.String,
}

# User API
class UserAPI(Resource):
    @auth_required("token")
    def get(self, username, password):
        login = db.session.query(User).filter_by(username=username).first()
        pword = db.session.query(User).filter_by(password=password).first()
        if login and pword:
            return {"username": login.username, "user_id": login.id}, 200
        else:
            return {"message": "User not found"}, 404

    def post(self):
        args = create_user_parser.parse_args()
        username = args.get("username")
        password = args.get("password")
        if not username or not password:
            return {"message": "Username and Password are required"}, 400
        user = User(username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created"}, 200

# Card API
class CardAPI(Resource):
    @auth_required("token")
    def get(self, cardId):
        card = db.session.query(Card).filter_by(card_id=cardId).first()
        if card:
            return marshal(card, card_resource_fields), 200
        else:
            return {"message": "Card not found"}, 404

    def post(self):
        args = create_card_parser.parse_args()
        card_name = args.get("card_name")
        card_value = args.get("card_value")
        if not card_name or not card_value:
            return {"message": "Invalid card data"}, 400
        card = Card(front=card_name, back=card_value)
        db.session.add(card)
        db.session.commit()
        return {"card_name": card.front, "card_value": card.back}, 200

    def put(self, cardId):
        args = update_card_parser.parse_args()
        card_new = args.get("card_new")
        card_value = args.get("card_value")
        card = db.session.query(Card).filter_by(card_id=cardId).first()
        if card:
            card.front = card_new
            card.back = card_value
            db.session.commit()
            return {"card_name": card.front, "card_value": card.back}, 200
        else:
            return {"message": "Card not found"}, 404

    def delete(self, cardId):
        card = db.session.query(Card).filter_by(card_id=cardId).first()
        if card:
            db.session.delete(card)
            db.session.commit()
            return {"message": "Card deleted"}, 200
        else:
            return {"message": "Card not found"}, 404

# Deck API
class DeckAPI(Resource):
    def get(self, username):
        user = db.session.query(User).filter_by(username=username).first()
        if not user:
            return {"message": "User not found"}, 404
        decks = db.session.query(Deck).filter_by(user_id=user.id).all()
        if decks:
            return [{"deck_name": deck.name, "deck_rate": deck.deck_rate} for deck in decks], 200
        else:
            return {"message": "No decks found"}, 404

    def put(self, deckId):
        args = update_deck_parser.parse_args()
        deck_new = args.get("deck_new")
        deck_value = args.get("deck_value")
        deck = db.session.query(Deck).filter_by(deck_id=deckId).first()
        if deck:
            deck.name = deck_new
            deck.deck_rate = deck_value
            db.session.commit()
            return {"deck_name": deck.name, "deck_rate": deck.deck_rate}, 200
        else:
            return {"message": "Deck not found"}, 404

    def delete(self, deckId):
        deck = db.session.query(Deck).filter_by(deck_id=deckId).first()
        if deck:
            db.session.delete(deck)
            db.session.commit()
            return {"message": "Deck deleted"}, 200
        else:
            return {"message": "Deck not found"}, 404

# Test API
test_api_resource_fields = {
    'msg': fields.String,
}

class TestAPI(Resource):
    def get(self):
        return marshal({"msg": "Hello World from TestAPI"}, test_api_resource_fields)

# Add Resources
# api.add_resource(UserAPI, "/api/user", "/api/user/login")
# api.add_resource(CardAPI, "/api/card/<int:cardId>")
# api.add_resource(DeckAPI, "/api/deck/<string:username>", "/api/deck/<int:deckId>")
# api.add_resource(TestAPI, "/api/test")
