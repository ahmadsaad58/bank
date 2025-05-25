from flask import Flask

from bank.api.accounts import accounts_bp
from bank.api.transactions import transactions_bp
from bank.api.users import users_bp
from bank.api.utilities import utilities_bp

from bank.api.data.data import load_data

load_data()

app = Flask(__name__)
app.register_blueprint(users_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(transactions_bp)
app.register_blueprint(utilities_bp)


@app.route("/", methods=["GET"])
def index() -> str:
    """Welcome message for the API.
    Returns:
        str: A welcome message.
    """
    return "Welcome to the Simple Bank API!"


# --- Run the application ---
if __name__ == "__main__":
    # When running in development, you can enable debug mode
    # app.run(debug=True) will automatically reload on code changes
    # and provide a debugger.
    app.run(debug=True, host="0.0.0.0", port=5001)
