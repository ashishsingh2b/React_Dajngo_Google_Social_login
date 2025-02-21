import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework.decorators import api_view
from google_auth_oauthlib.flow import Flow
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@api_view(["GET"])
def google_auth_url(request):
    """Generate the Google login URL"""
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=["openid", "email", "profile"],
        )
        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI
        authorization_url, _ = flow.authorization_url(prompt="consent")

        print(f"[INFO] Generated Google Auth URL: {authorization_url}")
        return JsonResponse({"authorization_url": authorization_url})

    except Exception as e:
        print(f"[ERROR] Failed to generate Google Auth URL: {str(e)}")
        return JsonResponse({"error": "Failed to generate authorization URL"}, status=500)


@api_view(["GET", "POST"])
def google_callback(request):
    """Handle Google OAuth callback"""
    try:
        code = request.GET.get("code") or request.data.get("code")
        if not code:
            print("[WARNING] No authorization code provided in request")
            return JsonResponse({"error": "No code provided"}, status=400)

        print(f"[INFO] Received authorization code: {code}")

        # OAuth token exchange
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }
        token_response = requests.post(token_url, data=token_data)
        token_response_json = token_response.json()

        print(f"[INFO] Token response: {token_response_json}")

        if "error" in token_response_json:
            print(f"[ERROR] Token exchange failed: {token_response_json}")
            return JsonResponse(token_response_json, status=400)

        access_token = token_response_json["access_token"]
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        userinfo = userinfo_response.json()

        print(f"[INFO] User info received: {userinfo}")

        # Create or update user
        user, created = User.objects.get_or_create(
            email=userinfo["email"],
            defaults={
                "username": userinfo["email"],
                "google_id": userinfo["id"],
                "first_name": userinfo.get("given_name", ""),
                "last_name": userinfo.get("family_name", ""),
            },
        )

        if created:
            print(f"[INFO] New user created: {user.email}")
        else:
            print(f"[INFO] Existing user logged in: {user.email}")

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        jwt_access_token = str(refresh.access_token)

        print(f"[INFO] Generated JWT token for user: {user.email}")

        return JsonResponse({
            "message": "Login successful",
            "user": userinfo,
            "token": jwt_access_token
        })

    except Exception as e:
        print(f"[ERROR] Authentication failed: {str(e)}")
        return JsonResponse({"error": "Authentication failed"}, status=500)
