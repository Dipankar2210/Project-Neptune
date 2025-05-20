from app import create_app

# This code creates and runs a Flask web application:
# 1. Imports the create_app factory function from the app package
# 2. Creates a Flask application instance by calling create_app()
# 3. Runs the application in debug mode when this file is run directly
#    (not when imported as a module)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 