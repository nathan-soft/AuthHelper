import click
import pyperclip
from commands import (
    set_default_profile,
    list_profiles,
    show_current,
    add_profile,
    remove_profile,
    status as show_status
)
from auth import run_login


class AuthGroup(click.Group):
    def invoke(self, ctx):
        try:
            return super().invoke(ctx)

        except click.ClickException:
            raise

        except Exception as ex:
            raise click.ClickException(str(ex)) from ex

@click.group(name="auth", cls=AuthGroup)
def cli():
    """Auth CLI tool"""
    pass


@cli.command()
@click.argument("profile", required=False)
@click.option("--copy", is_flag=True, help="Copy token to clipboard")
@click.option("--fresh", is_flag=True, help="Force a fresh login")
def login(profile, copy, fresh):
    token = run_login(profile, fresh=fresh)

    print("\nAccess Token:\n")
    print(token)

    if copy:
        pyperclip.copy(token)
        print("\nToken copied to clipboard!")

@cli.command()
def list():
    list_profiles()

@cli.command()
@click.argument("profile")
def use(profile):
    set_default_profile(profile)

@cli.command("add-profile")
def add_profile_command():
    add_profile()

@cli.command("remove-profile")
@click.argument("profile", required=False)
def remove_profile_command(profile):
    remove_profile(profile)

@cli.command()
def show():
    show_current()

@cli.command()
def status():
    show_status()
