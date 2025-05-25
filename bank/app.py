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


# --- Run the application ---
if __name__ == "__main__":
    # When running in development, you can enable debug mode
    # app.run(debug=True) will automatically reload on code changes
    # and provide a debugger.
    app.run(debug=True, host="0.0.0.0", port=5001)
