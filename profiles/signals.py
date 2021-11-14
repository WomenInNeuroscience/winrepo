from django.contrib.auth.signals import user_logged_in

def detect_first_login(sender, user, request, **kwargs):
    if user.last_login is None:
        request.session['first_login'] = True

user_logged_in.connect(detect_first_login)
