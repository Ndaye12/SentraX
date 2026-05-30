from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>SENTRAX API TEST</h1><p>Le serveur fonctionne correctement.</p>'

@app.route('/docs')
def docs():
    return '<h1>Documentation</h1><p>API endpoints disponibles</p>'

if __name__ == '__main__':
    print("Serveur démarré sur http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)