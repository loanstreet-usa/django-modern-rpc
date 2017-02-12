import base64

from django.contrib.auth import authenticate
from django.utils import six

from modernrpc import auth


def http_basic_auth_check_user(request, user_validation_func, *args):
    """
    Inspect the given request and extract the user / password from HTTP_AUTHORIZATION header.
    Then try to use it to authenticate against Django User model. If user can be authenticated, it is returned.
    If no user is found, an anonymous user object is returned.
    :param request: The request to inspect
    :param user_validation_func:
    :return:
    """
    return user_validation_func(http_basic_auth_get_user(request), *args)


def http_basic_auth_get_user(request):
    """Inspect the given request to find a logged user. If not found, the header HTTP_AUTHORIZATION
    is read for 'Basic Auth' login and password, and try to authenticate against default UserModel.
    Return a User instance (possibly anonymous, meaning authentication failed)"""

    # By default, let the AuthenticationMiddleware do the job
    current_user = getattr(request, 'user')

    if not current_user or current_user.is_anonymous():
        # This was grabbed from https://www.djangosnippets.org/snippets/243/
        # Thanks to http://stackoverflow.com/a/1087736/1887976
        if 'HTTP_AUTHORIZATION' in request.META:
            auth = request.META['HTTP_AUTHORIZATION'].split()
            if len(auth) == 2 and auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).decode('utf-8').split(':')
                current_user = authenticate(username=uname, password=passwd)

    return current_user


# Decorator
def http_basic_auth_login_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged users"""

    def decorated(function):
        return auth.set_authentication_predicate(function, http_basic_auth_check_user, [auth.user_is_logged])

    # If @http_basic_auth_login_required() is used (with parenthesis)
    if func is None:
        return decorated

    # If @http_basic_auth_login_required is used without parenthesis
    return decorated(func)


# Decorator
def http_basic_auth_superuser_required(func=None):
    """Decorator. Use it to specify a RPC method is available only to logged superusers"""
    def decorated(function):
        return auth.set_authentication_predicate(function, http_basic_auth_check_user, [auth.user_is_superuser])

    # If @http_basic_auth_superuser_required() is used (with parenthesis)
    if func is None:
        return decorated

    # If @http_basic_auth_superuser_required is used without parenthesis
    return decorated(func)


# Decorator
def http_basic_auth_permissions_required(permissions):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):
        if isinstance(permissions, six.string_types):
            # Check a single permission
            return auth.set_authentication_predicate(func, http_basic_auth_check_user,
                                                     [auth.user_has_perm, permissions])

        # Check many permissions
        return auth.set_authentication_predicate(func, http_basic_auth_check_user,
                                                 [auth.user_has_perms, permissions])
    return decorated


# Decorator
def http_basic_auth_group_member_required(groups):
    """Decorator. Use it to specify a RPC method is available only to logged users with given permissions"""
    def decorated(func):

        if isinstance(groups, six.string_types):
            # Check user is in a group
            return auth.set_authentication_predicate(func, http_basic_auth_check_user, [auth.user_in_group, groups])

        # Check user is in many group
        return auth.set_authentication_predicate(func, http_basic_auth_check_user, [auth.user_in_groups, groups])

    return decorated