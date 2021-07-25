import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, db
from .auth.auth import AuthError, requires_auth, get_token_auth_header

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()

## ROUTES
'''
@ implement endpoint
@Insert permissions
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['GET'])
def getting_drinks():
   
    try:
        

        drinks_data = db.session.query(Drink).all()
        drinks =[]
              
        for each in drinks_data:

            drinks.append({
                "id":each.id,
                "title":each.title,
                "recipe":each.recipe}
            )
        
    except:

        abort(500)
       
    finally:
        db.session.close()

    return jsonify({"success": True, "drinks": drinks}),200


'''
@ implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def getting_drinks_deatils(auth):

    #  Setup structure for drinks 
    try:
        print(auth)
        if not auth['iss']:
            print('not null')

        drinks_data = db.session.query(Drink).all()
        drinks = []
       # print(drinks_data)
        for each in drinks_data:
        
            drinks.append({
                "id":each.id,
                "title":each.title,
                "recipe":each.recipe}
            )
        
    except:
        abort(500)

    finally:
        db.session.close()

    return jsonify({"success": True, "drinks": drinks}),200

'''
@implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        @TODO it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def posting_drinks(auth):
    # @ToDO: Setup structure for drinks 
    try:
        
        data = request.get_json()
        recipe = json.dumps(data['recipe'])
        
        drink = Drink(title=data['title'], recipe=recipe)

        db.session.add(drink)
        db.session.commit()
    except: 
        db.session.rollback()
        abort(400)
    
    finally:
      
      db.session.close()

    return jsonify({"success": True, "drinks": data}), 200

'''
@ implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
       @TODO it should require the 'patch:drinks' permission--> testing
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(auth, id):
   
    try:
        data = request.get_json()
        
        print(id)

        drink = Drink.query.get(id)

        longdrink = drink.long()

        longdrink['title'] = data['title']
        longdrink['recipe'] = data['recipe']

        db.session.commit()

    except:
        db.session.rollback()
        abort(404)

    finally:
        db.session.close()
    
    return jsonify({"success": True, "drinks": [longdrink]}),200

'''
@ implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        @TODO it should require the 'delete:drinks' permission --> testing
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def deletion_drinks(auth, id):
   
    try:
         
        drink = Drink.query.get(id)
        db.session.delete(drink)
        db.session.commit()

    except:
        abort(404)
        db.session.rollback()

    finally:
        db.session.close()

    return jsonify({"success": True, "delete": id}),200

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@ implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(500)
def servererror(error):
    return jsonify({"success": False, "error": 500,"message": "internal server error"}),500
  
@app.errorhandler(400)
def badrequest(error):
    return jsonify({
                    "success": False, 
                    "error": 400,
                    "message": "bad request"
                    }), 400
  
'''
@ implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def unprocessable_entity(error):
    return  jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@ implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(401)
def unprocessable_entity(error):
    return  jsonify({
                    "success": False, 
                    "error": 401,
                    "message": "not authorized"
                    }), 401

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response