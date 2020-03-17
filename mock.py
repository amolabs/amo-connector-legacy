import flask
from flask_restful import reqparse, Resource, Api
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC

private_key = ECC.generate(curve="P-256")
public_key = private_key.public_key()


class MockStorage(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('owner', type=str, required=True)
        parser.add_argument('metadata', type=dict, required=True)
        parser.add_argument('data', type=str, required=True)

        args = parser.parse_args()

        hasher = SHA256.new(bytes.fromhex(args['data']))
        hasher.update(args['metadata']['path'].encode())
        hasher.update(args['metadata']['name'].encode())

        parcel_id = hasher.digest().hex()

        return {
            'id': parcel_id,
        }


app = flask.Flask("MockStorage")
api = Api(app)
api.add_resource(MockStorage, '/api/v1/parcels')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
