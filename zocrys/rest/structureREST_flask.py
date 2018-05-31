import flask
VERSION = 1

app = flask.Flask(__name__)

@app.route('/v{:d}/distances/'.format(VERSION), methods=['GET'])
def distances() -> dict:
    args = flask.request.args
    structures = flask.json.loads(args.pop('structures'))
    method = args.pop('method')
    settings = flask.json.loads(args.pop('settings'))
    input = {
        'structures': structures,
        'method': method,
        'settings': settings,
        'args': args
    }
    return flask.jsonify(input)
    # flask.abort(501)

@app.route('/v{:d}/distances2/<args>'.format(VERSION))
def distances2(args: str) -> dict:
    args = flask.json.loads(args)
    structures = args.pop('structures')
    method = args.pop('method')
    settings = args.pop('settings')
    input = {
        'structures': structures,
        'method': method,
        'settings': settings
    }
    return flask.jsonify(input)
    # flask.abort(501)

@app.route('/v{:d}/comparisons'.format(VERSION))
def comparisons():
    flask.abort(501)

@app.route('/v{:d}/fingerprints'.format(VERSION))
def fingerprints():
    flask.abort(501)

@app.route('/v{:d}/prototypes'.format(VERSION))
def prototypes():
    flask.abort(501)

if __name__ == '__main__':
    app.run(debug=True)