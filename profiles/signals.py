from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in


def detect_first_login(sender, user, request, **kwargs):
    # ``last_login`` is None only on a user's very first login. Django's own
    # ``update_last_login`` receiver overwrites it on every login, so ours
    # must observe the value *before* that happens (see ordering below).
    if user.last_login is None:
        request.session['first_login'] = True


# Django has no receiver-priority API. Rather than blindly rotating the whole
# ``user_logged_in`` receiver list (the previous approach, which also disturbed
# unrelated receivers such as allauth's), order only the two receivers we care
# about: drop Django's built-in updater, connect ours, then reconnect the
# updater so it runs afterwards. dispatch_uids keep this idempotent.
user_logged_in.disconnect(dispatch_uid="update_last_login")
user_logged_in.connect(
    detect_first_login, dispatch_uid="profiles.detect_first_login"
)
user_logged_in.connect(update_last_login, dispatch_uid="update_last_login")
