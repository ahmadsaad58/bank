from flasgger import Swagger
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from bank.api.accounts import accounts_bp
from bank.api.data.data import load_data
from bank.api.transactions import transactions_bp
from bank.api.users import users_bp
from bank.api.utilities import utilities_bp

load_data()

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    # TODO: Configure the rate limit
    default_limits=["100 per hour"],  
)
swagger = Swagger(app)
app.register_blueprint(users_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(utilities_bp)


@app.route("/", methods=["GET"])
def index() -> str:
    """Welcome message for the API.
    ---
    tags:
      - Home
    responses:
        200:
            description: A welcome message for the API.
    """
    return "Welcome to the Simple Bank API!"

@app.route("/health", methods=["GET"])
@limiter.limit("10 per second")
def health_check() -> str:
    """Health check endpoint to verify the API is running.
    ---
    tags:
      - Health Check
    responses:
        200:
            description: A message indicating the API is healthy.
        503:
            description: Service Unavailable if the API is not healthy.
    """
    return "API is healthy!", 200

@app.route("/ping", methods=["GET"])
def ping() -> str:
    """Ping endpoint to check if the API is responsive.
    ---
    tags:
      - Ping
    responses:
        200:
            description: A message indicating the API is responsive.
    """
    return "Pong!", 200


# --- Run the application ---
if __name__ == "__main__":
    # When running in development, you can enable debug mode
    # app.run(debug=True) will automatically reload on code changes
    # and provide a debugger.
    app.run(debug=True, host="0.0.0.0", port=5001)
