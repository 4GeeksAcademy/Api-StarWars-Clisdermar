"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Personaje, Planeta,FavoritePlaneta, FavoritePersonaje
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
#from models import Person

app = Flask(__name__)
# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)


app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def handle_hello():
    users = User.query.all()

    response_body = [user.serialize() for user in users]

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_personajes():
  
    personajes = Personaje.query.all()

    # Serializar los personajes y crear una lista de diccionarios
    serialized_personajes = [personaje.serialize() for personaje in personajes]

    # Devolver la lista de personajes como una respuesta JSON
    return jsonify(serialized_personajes), 200


@app.route('/people/<int:people_id>', methods=['GET'])
def get_Onepersonaje(people_id):

    personaje = Personaje.query.get(people_id)
    
    if personaje: 
        serialized_personaje = personaje.serialize()
        return jsonify(serialized_personaje), 200
    else:
        return jsonify({'message': 'Personaje no encontrado'}), 404


@app.route('/planets', methods =['GET'])
def get_planeta():
    planets = Planeta.query.all()

    response_body = [planet.serialize() for planet in planets]

    return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_Oneplaneta(planet_id):

    planeta = Planeta.query.get(planet_id)
    
    if planeta: 
        serialized_planeta = planeta.serialize()
        return jsonify(serialized_planeta), 200
    else:
        return jsonify({'message': 'Planeta no encontrado'}), 404
    
@app.route("/login", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    # Consulta la base de datos por el email de usuario y la contraseña
    user = User.query.filter_by(email=email, password=password).first()

    if user is None:
        # el usuario no se encontró en la base de datos
        return jsonify({"msg": "Bad email or password"}), 401
    
    # Crea un nuevo token con el id de usuario dentro
    access_token = create_access_token(identity=user.email)
    return jsonify({ "token": access_token, "user_id": user.id})


# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.

@app.route("/users/favorites", methods=["GET"])
@jwt_required()
def get_current_users_favorites():

    current_user_email = get_jwt_identity()

    current_user = User.query.filter_by(email=current_user_email).first()

    if current_user is None:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Serializa los favoritos y devuelve la respuesta en formato JSON
    return jsonify(current_user.serialize()), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_new_fav_planet(planet_id):
    user = User.query.first()    
    if user:
        planet = Planeta.query.get(planet_id)
        if planet:
            fav = FavoritePlaneta(user_id = user.id, planeta_id = planet_id) #crea una nueva instancia de favoritoPlanea
            db.session.add(fav)
            db.session.commit()
            return jsonify({'msg': 'Planet added successfully'}), 200
        else: return jsonify({'msg': 'Planet not found'}), 404
    else: return jsonify({'msg': 'User not found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_new_fav_personaje(people_id):
    user = User.query.first()    
    if user:
        personaje = Personaje.query.get(people_id)
        if personaje:
            fav = FavoritePersonaje(user_id = user.id, personaje_id = people_id) #crea una nueva instancia de favoritoPlanea
            db.session.add(fav)
            db.session.commit()
            return jsonify({'msg': 'Personaje added successfully'}), 200
        else: return jsonify({'msg': 'Personaje not found'}), 404
    else: return jsonify({'msg': 'User not found'}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_personaje(people_id):
    favorite = FavoritePersonaje.query.filter_by(personaje_id=people_id).first()
    if favorite is None:
        return jsonify({'msg': 'Personaje not found'}), 404
    else:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": f"Personaje {favorite.personaje_id} deleted"}),200
    
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_planeta(planet_id):
    favorite = FavoritePlaneta.query.filter_by(planeta_id=planet_id).first()
    if favorite is None:
        return jsonify({'msg': 'Planeta not found'}), 404
    else:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"msg": f"Planeta {favorite.planeta_id} deleted"}),200
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
