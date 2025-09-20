from django.contrib.sessions.models import Session
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import render

class LimitConcurrentSessionsMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If user is not authenticated, check for timeout flag
        if not request.user.is_authenticated:
            if request.session.get('timed_out', False):
                # Remove the flag so it only shows once
                request.session.pop('timed_out')
                return render(request, 'session_timeout.html', status=401)
            return

        # ...existing concurrent session logic...

        # Check for session expiry (inactivity handled by Django)
        # If session is about to expire, set the flag
        last_activity = request.session.get('last_activity')
        now = timezone.now().timestamp()
        if last_activity and now - last_activity > settings.SESSION_COOKIE_AGE:
            request.session['timed_out'] = True
            logout(request)
            return render(request, 'session_timeout.html', status=401)
        # Update last activity timestamp
        request.session['last_activity'] = now