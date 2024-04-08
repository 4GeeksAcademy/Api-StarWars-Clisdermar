from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import create_engine



db = SQLAlchemy()

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password = db.Column(db.String(80), unique=False, nullable=False)
  is_active = db.Column(db.Boolean(), unique=False, nullable=False)

  def __init__(self, id, email, password, is_active):
      self.id = id
      self.email = email
      self.password = password
      self.is_active = is_active

  def __repr__(self):
    return '<User %r>' % self.email

  def serialize(self):
    return {
        "id": self.id,
        "email": self.email,
        "favorite_planetas_ref": [favorite.serialize() for favorite in self.favorite_planetas_ref] if self.favorite_planetas_ref else None,
        "favorite_personaje_ref": [favorite.serialize() for favorite in self.favorite_personaje_ref] if self.favorite_personaje_ref else None
        # # No serializar la contraseña, es un riesgo de seguridad
    }
class Personaje(db.Model):
    __tablename__ = 'personaje' 
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(250),nullable = False)
  
    
    def __init__(self,id,name):
       self.id = id
       self.name = name
             

    def __repr__(self):
        return '<Personaje %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
           
          
            # do not serialize the password, its a security breach
        }
    
class Planeta(db.Model):
    __tablename__ = 'planeta'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    
    
    def __init__(self, id,name):
       self.id = id
       self.name = name
           

    def __repr__(self):
        return f'<Planeta name: {self.name}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
           
        }

class FavoritePlaneta(db.Model):
     __tablename__ = 'favorite_planeta'
     id = db.Column(db.Integer, primary_key = True)

    
     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     user = relationship('User', backref='favorite_planetas_ref')

     planeta_id = db.Column(db.Integer, db.ForeignKey('planeta.id'), nullable=True)
     planeta = relationship('Planeta')

     
     def __repr__(self):
         return f'<FavoritePlaneta id:{self.id}, user_id:{self.user_id}, planeta_id:{self.planeta_id}>'

     def serialize(self):
         return {
             "id": self.id,
             "user_id": self.user_id,
             "planeta_id": self.planeta_id
         }

class FavoritePersonaje(db.Model):
     __tablename__ = 'favorite_personaje'
     id = db.Column(db.Integer, primary_key = True)

     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
     user = relationship('User', backref='favorite_personaje_ref')


     personaje_id = db.Column(db.Integer, ForeignKey('personaje.id'), nullable=True)
     personaje = relationship('Personaje') 
    
     def __repr__(self):
         
         return f'<FavoritePersonaje id:{self.id}, user_id:{self.user_id}, personaje_id:{self.personaje_id}>'

     def serialize(self):
         return {
            "id": self.id,
            "user_id": self.user_id,
            "personaje_id": self.personaje_id
         }