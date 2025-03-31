from flask_migrate import Migrate
from flask_migrate import init as db_init_command
from flask_migrate import migrate as db_migrate_command
from flask_migrate import upgrade as db_upgrade_command
from flask_migrate import downgrade as db_downgrade_command
from flask_migrate import history as db_history_command
from app import create_app, db
import click
import os

app = create_app()
migrate = Migrate(app, db)

@app.cli.command("db_init")
def db_init():
    """Initialize the database migrations."""
    click.echo("Initializing the database migrations...")
    db_init_command(directory='migrations')

@app.cli.command("db_migrate")
@click.option("--message", "-m", help="Migration message")
def db_migrate(message):
    """Create a new migration."""
    if message:
        click.echo(f"Creating a new migration with message: {message}")
        db_migrate_command(message=message, directory='migrations')
    else:
        click.echo("Creating a new migration...")
        db_migrate_command(directory='migrations')

@app.cli.command("db_upgrade")
def db_upgrade():
    """Apply all available migrations."""
    click.echo("Applying migrations...")
    db_upgrade_command(directory='migrations')

@app.cli.command("db_downgrade")
def db_downgrade():
    """Revert the last migration."""
    click.echo("Reverting the last migration...")
    db_downgrade_command(directory='migrations')

@app.cli.command("db_history")
def db_history():
    """Show migration history."""
    # The migration history is already displayed by the Flask-Migrate CLI
    # We don't need to add anything here
    pass

if __name__ == '__main__':
    app.run() 