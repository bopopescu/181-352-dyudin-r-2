from flask import request, render_template, session, flash, redirect, url_for
import flask_login

ADMIN_ROLE_ID = 1

def is_admin():
    return flask_login.current_user.role_id == ADMIN_ROLE_ID


class UsersPolicy:
    def __init__(self, record=None):
        self.record = record

    def new(self):
        return is_admin()

    def delete(self):
        return is_admin()

    def edit(self):
        is_editing_user = flask_login.current_user.id == self.record.id
        return is_admin() or is_editing_user


class User(flask_login.UserMixin):
    def can(self, action, record=None):
        policy = UsersPolicy(record=record)
        method = getattr(policy, action, None)
        if method:
            return method()
        return False