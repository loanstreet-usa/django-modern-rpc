# coding: utf-8
from django.contrib.auth.models import Group
from django.utils import six


# Decorator
def set_authentication_predicate(rpc_method, predicate, params=None):
    """
    Assign a new authentication predicate to an RPC method.
    This is the most generic decorator used to implement authentication.
    Predicate is a standard function with the following signature:

    .. code:: python

       def my_predicate(request, *params):
           # Inspect request and extract required information

           if <condition>:
               # The condition to execute the method are met
               return True
           return False

    :param rpc_method:
    :param predicate:
    :param params:
    :return:
    """
    if hasattr(rpc_method, 'modernrpc_auth_predicates'):
        rpc_method.modernrpc_auth_predicates.append(predicate)
        rpc_method.modernrpc_auth_predicates_params.append(params)

    else:
        rpc_method.modernrpc_auth_predicates = [predicate]
        rpc_method.modernrpc_auth_predicates_params = [params]

    return rpc_method


def user_is_logged(user):
    return not user.is_anonymous()


def user_is_superuser(user):
    return user.is_superuser


def user_has_perm(user, perm):
    return user_is_superuser(user) or user.has_perm(perm)


def user_has_all_perms(user, perms):
    """Returns True if the given user have all given permissions"""
    return user_is_superuser(user) or user.has_perms(perms)


def user_has_any_perm(user, perms):
    return user_is_superuser(user) or any(user_has_perm(user, perm) for perm in perms)


def user_in_group(user, group):
    """Returns True if the given user is in given group"""
    if isinstance(group, Group):
        return user_is_superuser(user) or group in user.groups.all()
    elif isinstance(group, six.string_types):
        return user_is_superuser(user) or user.groups.filter(name=group).exists()
    raise TypeError("'group' argument must be a string or a Group instance")


def user_in_any_group(user, groups):
    """Returns True if the given user is in at leats 1 of the given groups"""
    return user_is_superuser(user) or any(user_in_group(user, group) for group in groups)


def user_in_all_groups(user, groups):
    """Returns True if the given user is in all given groups"""
    return user_is_superuser(user) or all(user_in_group(user, group) for group in groups)
