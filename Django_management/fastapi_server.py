from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .my_gradio_app import gradio_app_asgi # Import the app from the file above

# --- CONFIGURATION ---
# 💡 IMPORTANT: Verify these paths match your Django setup!
DJANGO_LOGIN_URL = "/accounts/login/" # Your actual Django login URL path (e.g., /admin/login/)
GRADIO_PATH = "/gradio" # The path where Gradio will be mounted (e.g., http://127.0.0.1:8001/gradio/)

app = FastAPI()

# --- Custom Django Session Validation Middleware (The Gatekeeper) ---
class DjangoSessionAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        # 1. Check if the requested path is the protected Gradio app path
        is_protected_path = request.url.path.startswith(GRADIO_PATH)

        if is_protected_path:
            # 2. Look for the Django session cookie
            # The 'sessionid' is the default name Django uses for its session cookie.
            session_id = request.cookies.get('sessionid')
            
            # NOTE ON SECURITY: This only checks for the *existence* of the cookie.
            # For a truly secure production environment, you would need to write 
            # code here to VALIDATE the session_id against Django's database 
            # to ensure the session is active and valid.
            if not session_id:
                # 3. If unauthorized, redirect to Django login.
                # Use the 'next' parameter so Django knows where to redirect after login.
                redirect_url = f"http://127.0.0.1:8000{DJANGO_LOGIN_URL}?next=/dashboard{GRADIO_PATH}/"
                
                # We use the full URL here because the redirect goes back to the Django server (port 8000)
                return RedirectResponse(url=redirect_url, status_code=302)

        # 4. If the cookie is present (or path is not protected), proceed to the Gradio app
        response = await call_next(request)
        return response

# Apply the middleware to the FastAPI app
app.add_middleware(DjangoSessionAuthMiddleware)

# --- Mount the Gradio Application ---
# The Gradio app is now served and protected under the specified path.
app.mount(GRADIO_PATH, gradio_app_asgi)