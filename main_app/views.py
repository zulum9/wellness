import datetime
import hashlib
import json
import random
import traceback

import requests
from decouple import config
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django_countries import countries
from google import genai

from .models import AppUser, DailyUplift, GratitudeThought, SupportGroup

# --- AI CONFIGURATION ---
API_KEY = config("GEMINI_API_KEY", default="")
# Use gemini-1.5-flash for the best balance of speed and cost
client = genai.Client(api_key=API_KEY) if API_KEY else None


@login_required
@csrf_exempt
def sister_chatbot_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message", "")

            # Here you drop in your backend API call (e.g., OpenAI, Gemini, etc.)
            # We configure a strict, highly empathetic system prompt.
            system_prompt = (
                "You are an incredibly warm, deeply empathetic, loving, and non-judgmental friend/sister "
                "supporting women inside the 'Beyond Survival Sisterhood' community. A user is reaching out with personal problems. "
                "Listen deeply, provide absolute psychological comfort, validation, and safe counsel. Keep your responses thoughtful, "
                "restorative, and companionable. Avoid sounding clinical or detached."
            )

            # --- Simulated integration response ---
            # response = client.chat.completions.create(..., messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}])
            # bot_reply = response.choices[0].message.content

            bot_reply = f"Thank you for sharing that with me, sis. I hear you completely, and I'm right here with you. Step by step, we will get through this. Remember that you are resilient and deeply valued."

            return JsonResponse({"reply": bot_reply})
        except Exception as e:
            return JsonResponse({"error": "Could not process request"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def logout_view(request):
    """Logs out the user and safely redirects back to the welcome landing page."""
    auth_logout(request)
    return redirect("index")


@login_required
def groups_view(request):
    """Fetches real-time support group data configured by the system administrator."""
    # Pulls all rows created via your admin site panel
    db_groups = SupportGroup.objects.all()

    return render(request, "main_app/groups.html", {"categories": db_groups})


@login_required
def groupss_view(request):
    """Renders the community support groups interface segmented by emotional needs."""
    # Group categories customized for emotional and mental sanctuary spaces
    support_categories = [
        {
            "name": "Anxiety Sanctuary",
            "slug": "anxious",
            "description": "A calm, grounding space to share breathing techniques, mindful management, and find peace together.",
            "icon": "✨",
        },
        {
            "name": "Hope & Light Circle",
            "slug": "sad",
            "description": "A uplifting community focused on gentle encouragement, processing heavy days, and mutual comfort.",
            "icon": "🌱",
        },
        {
            "name": "The Connected Sisterhood",
            "slug": "lonely",
            "description": "A warm, interactive collective dedicated to building deep relationships, sharing stories, and defeating isolation.",
            "icon": "🤝",
        },
    ]

    return render(request, "main_app/groups.html", {"categories": support_categories})


# Ensure your client is initialized at the top of the file:
# from google import genai
# client = genai.Client()


def get_ai_explanation(prompt_text):
    """Generates an AI reflection using the highly available Gemini 2.0 Flash stable model."""
    if not prompt_text:
        return "Take a moment to let this message resonate with your spirit."

    # 1. Check Django cache first to protect your API quota
    text_hash = hashlib.md5(prompt_text.encode()).hexdigest()
    cache_key = f"ai_reflection_{text_hash}"
    cached_res = cache.get(cache_key)
    if cached_res:
        return cached_res

    # Predefined high-quality backups if the API experiences temporary latency or downtime
    fallback_reflections = [
        "Peace begins with a quiet mind. Let these words settle gently into your heart and guide your path today.",
        "You are operating with grace and building remarkable strength. Give yourself permission to pause and breathe.",
        "Every step you take is a testament to your resilience. Trust the timing of your unique journey.",
        "Look inward for the clarity you seek. Your inner compass already knows the way forward.",
        "May these words remind you of your inherent worth. You are fully capable of handling whatever today brings.",
    ]

    if not client:
        return random.choice(fallback_reflections)

    try:
        # FIX: Using the correct, modern stable 2.0 identifier
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                f"Provide a 2-sentence comforting, soulful reflection for a women's wellness app regarding: {prompt_text}"
            ],
        )
        explanation = response.text.strip()

        # Cache successful API results for 24 hours
        cache.set(cache_key, explanation, 86400)
        return explanation

    except Exception as e:
        # Logs errors quietly in your terminal without breaking the client interface
        print(f"Gemini API Error intercepted: {e}")

        fallback = random.choice(fallback_reflections)
        # Cache the fallback for 5 minutes to manage the cooldown window smoothly
        cache.set(cache_key, fallback, 300)
        return fallback


def fetch_explanation(request):
    """API endpoint to deliver clean JSON data directly to JavaScript fetch operations."""
    text_to_explain = request.GET.get("text", "")
    explanation = get_ai_explanation(text_to_explain)

    # Always return JSON to keep the frontend fetch calls happy and error-free
    return JsonResponse({"explanation": explanation})


# _______________________


# --- API HELPERS ---
def fetch_daily_data():
    """Fetches all external API data with fallbacks and caching."""
    cache_key = f"daily_sanctuary_data_{datetime.date.today()}"
    data = cache.get(cache_key)

    if not data:
        # 1. Bible Verse
        try:
            res = requests.get("https://bible-api.com/data/web/random", timeout=3)
            v = res.json().get("random_verse", {})
            inspiration = f"{v.get('text', '').strip()} - {v.get('book')} {v.get('chapter')}:{v.get('verse')}"
        except:
            inspiration = "Be still, and know that I am God. - Psalm 46:10"

        # 2. Affirmation
        try:
            res = requests.get("https://www.affirmations.dev/", timeout=3)
            affirmation = res.json().get("affirmation")
        except:
            affirmation = "I am strong, capable, and worthy."

        # 3. Wellness & Gratitude Prompt
        try:
            res = requests.get("https://api.adviceslip.com/advice", timeout=3)
            advice = res.json().get("slip", {}).get("advice")
        except:
            advice = "Take a deep breath and stay present in this moment."

        # 4. Intention (Wisdom Quote)
        try:
            res = requests.get("https://api.quotable.io/random?tags=wisdom", timeout=3)
            intention = res.json().get("content", "I choose to lead with grace.")
        except:
            intention = "I choose to lead with grace and build strength."

        data = {
            "daily_inspiration": inspiration,
            "daily_affirmation": affirmation,
            "daily_wellness_tip": advice,
            "daily_intention": intention,
            "gratitude_prompt": f"What are you thankful for regarding: {advice}",
        }
        cache.set(cache_key, data, 86400)  # Cache until tomorrow

    return data


# --- VIEW FUNCTIONS ---


def index(request):
    return render(request, "main_app/index.html")


def dashboard_view(request):
    """Main dashboard logic handling display and thought saving."""
    # 1. Fetch Daily Content
    daily_data = fetch_daily_data()

    # 2. Handle Thought Submission
    if request.method == "POST" and "save_thought" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "Please sign up to save your reflections.")
            return redirect("signup_view")

        thought_text = request.POST.get("thought")
        active_prompt = request.POST.get("active_prompt")

        if thought_text:
            GratitudeThought.objects.create(
                user=request.user, prompt=active_prompt, thought=thought_text
            )
            messages.success(
                request, "Your reflection has been saved to your sanctuary."
            )
            return redirect("dashboard")

    # 3. Get User Context
    user_name = request.user.first_name if request.user.is_authenticated else "Guest"
    previous_thoughts = []
    if request.user.is_authenticated:
        previous_thoughts = GratitudeThought.objects.filter(user=request.user).order_by(
            "-created_at"
        )

    context = {
        "user_name": user_name,
        "today_full": now().strftime("%A").upper(),
        "previous_thoughts": previous_thoughts,
        **daily_data,
    }
    return render(request, "main_app/dashboard.html", context)


def chatbot_response(request):
    """HTMX endpoint for the 'How are you feeling' interaction."""
    mood = request.GET.get("mood")

    responses = {
        "anxious": {
            "message": "Take a deep breath. You are capable and strong.",
            "scripture": "Philippians 4:6-7",
            "action": "Try the 4-7-8 breathing exercise: In for 4, hold for 7, out for 8.",
        },
        "sad": {
            "message": "It's okay to not be okay. Your feelings are valid.",
            "scripture": "Psalm 34:18",
            "action": "Consider sharing your heart in one of our support groups.",
        },
        "lonely": {
            "message": "You are not alone in this journey.",
            "scripture": "Matthew 28:20",
            "action": "Browse our community boards to connect with others.",
        },
    }

    selected = responses.get(
        mood, {"message": "I am here to support you. How can I help?"}
    )
    return render(request, "main_app/chatbot_partial.html", {"response": selected})


def signup_view2(request):
    """Handles new user registration."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        age = request.POST.get("age")
        country = request.POST.get("country")

        try:
            user = AppUser.objects.create_user(
                username=email, email=email, first_name=name, age=age, country=country
            )
            login(request, user)
            wants_notifications = (
                request.POST.get("notifications") == "on"
                or request.POST.get("notifications") == True
            )

            if wants_notifications:
                try:
                    subject = "Your First Daily Oasis | The Mindful Queen"
                    message = (
                        f"Dearest Sister,\n\n"
                        f"Welcome to your sanctuary. Because you chose to activate daily reminders, "
                        f"here is your structural anchor for today:\n\n"
                        f"📖 BIBLE SCRIPTURE\n"
                        f"\"For I know the plans I have for you,' declares the Lord, 'plans to prosper you "
                        f'and not to harm you, plans to give you hope and a future."\n— Jeremiah 29:11\n\n'
                        f"✨ DAILY AFFIRMATION\n"
                        f'"I am not defined by my anxieties or heavy days. I am deeply loved, securely held, '
                        f'and stepping into my royalty step-by-step."\n\n'
                        f"🌱 INSPIRATION\n"
                        f"Remember that even the most beautiful roses require time in the dark soil before reaching "
                        f"toward the light. Your current season is not your final destination.\n\n"
                        f"🎯 TODAY'S INTENTION\n"
                        f'"Today, I will protect my peace, breathe deeply through moments of tension, and accept '
                        f'grace for my shortcomings."\n\n'
                        f"With all our love,\n"
                        f"The Mindful Queen Sisterhood"
                    )

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email="noreply@themindfulqueen.com",
                        recipient_list=[user.email],
                        fail_silently=True,  # Prevents application crashes if SMTP credentials aren't set yet
                    )
                except Exception:
                    pass
            return redirect("dashboard")
        except Exception:
            return render(
                request,
                "main_app/signup.html",
                {"error": "This email is already in use.", "countries": countries},
            )

    return render(request, "main_app/signup.html", {"countries": countries})


# main_app/views.py


def signup_view3(request):
    """Handles new user registration safely with proper auth creation."""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get(
            "password"
        )  # <--- 1. Capture the password from your HTML input field
        age = request.POST.get("age") or None
        country = request.POST.get("country")

        if not email or not password:
            return render(
                request,
                "main_app/signup.html",
                {
                    "error": "Please provide both an email and a password.",
                    "countries": countries,
                },
            )

        try:
            # 2. Use create_user with password handling so encryption takes place automatically
            user = AppUser.objects.create_user(
                username=email,
                email=email,
                password=password,  # <--- Crucial fix
                first_name=name,
                age=age,
                country=country,
            )

            # Formally log the new user session into the application cache
            login(request, user)

            wants_notifications = (
                request.POST.get("notifications") == "on"
                or request.POST.get("notifications") is True
            )

            if wants_notifications:
                try:
                    subject = "Your First Daily Oasis | Beyond Survival Sisterhood"
                    message = (
                        f"Dearest Sister,\n\n"
                        f"Welcome to your sanctuary. Because you chose to activate daily reminders, "
                        f"here is your structural anchor for today:\n\n"
                        f"📖 BIBLE SCRIPTURE\n"
                        f"\"For I know the plans I have for you,' declares the Lord, 'plans to prosper you "
                        f'and not to harm you, plans to give you hope and a future."\n— Jeremiah 29:11\n\n'
                        f"✨ DAILY AFFIRMATION\n"
                        f'"I am not defined by my anxieties or heavy days. I am deeply loved, securely held, '
                        f'and stepping into my sanctuary step-by-step."\n\n'
                        f"With all our love,\n"
                        f"Beyond Survival Sisterhood Team"
                    )

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,  # Keeps signup working even if your email server is offline
                    )
                except Exception:
                    pass

            return redirect("dashboard")

        except Exception as e:
            # Helps you see the actual underlying database or signal error in your server logs
            print(f"Signup Database Exception intercepted: {str(e)}")
            return render(
                request,
                "main_app/signup.html",
                {
                    "error": "This email is already registered or an error occurred. Please try again.",
                    "countries": countries,
                },
            )

    return render(request, "main_app/signup.html", {"countries": countries})


# main_app/views.py


def signup_view4(request):
    """Handles new user registration safely with notification saving and error isolation."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    # Assuming 'countries' is defined or imported at the top of your file
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        age = request.POST.get("age") or None
        country = request.POST.get("country")

        if not email or not password:
            return render(
                request,
                "main_app/signup.html",
                {
                    "error": "Please provide both an email and a password.",
                    "countries": countries,
                },
            )

        try:
            # 1. Capture the checkbox status upfront
            has_opted_in = request.POST.get("notifications") == "on"

            # 2. Pass the checkbox boolean value directly into user creation
            user = AppUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                age=age,
                country=country,
                wants_notifications=has_opted_in,  # <--- FIX 1: Saves to the DB field directly
            )

            # Establish the logged-in session for the browser cache
            login(request, user)

            # 3. CRUCIAL FIX 2: Isolate the send_mail code in its own separate try block
            # This ensures Gmail authentication crashes will never ruin a successful user signup!
            if has_opted_in:
                try:
                    subject = "Your First Daily Oasis | Beyond Survival Sisterhood"
                    message = (
                        f"Dearest Sister,\n\n"
                        f"Welcome to your sanctuary. Because you chose to activate daily reminders, "
                        f"here is your structural anchor for today:\n\n"
                        f"📖 BIBLE SCRIPTURE\n"
                        f"\"For I know the plans I have for you,' declares the Lord, 'plans to prosper you "
                        f'and not to harm you, plans to give you hope and a future."\n— Jeremiah 29:11\n\n'
                        f"✨ DAILY AFFIRMATION\n"
                        f'"I am not defined by my anxieties or heavy days. I am deeply loved, securely held, '
                        f'and stepping into my sanctuary step-by-step."\n\n'
                        f"With all our love,\n"
                        f"Beyond Survival Sisterhood Team"
                    )

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,  # Keeps execution smooth if email network drops
                    )
                except Exception as email_err:
                    # Log the email credentials issue to your console terminal
                    print(
                        f"Email server error caught safely (User was still created successfully): {str(email_err)}"
                    )

            # Clear step forward straight to your application workspace dashboard
            return redirect("dashboard")

        except Exception as db_err:
            # Now, this block ONLY catches genuine database exceptions (like an email duplicate)
            print(f"Signup Database Exception intercepted: {str(db_err)}")
            return render(
                request,
                "main_app/signup.html",
                {
                    "error": "This email is already registered. Please try logging in.",
                    "countries": countries,
                },
            )

    return render(request, "main_app/signup.html", {"countries": countries})


def signup_view(request):
    """
    Handles new user registration with explicit checkpoint tracking to trace backend dropouts.
    """
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        print("\n=== [CHECKPOINT 1] FORM SUBMISSION RECEIVED ===")
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        age = request.POST.get("age") or None
        country = request.POST.get("country")
        has_opted_in = request.POST.get("notifications") == "on"

        print(
            f"Captured Data -> Name: {name}, Email: {email}, Age: {age}, Country: {country}, Opt-In: {has_opted_in}"
        )

        if not email or not password:
            print("[-] Validation Failed: Missing Email or Password field.")
            return render(
                request,
                "main_app/signup.html",
                {
                    "error": "Please provide both an email and a password.",
                    "countries": countries,
                },
            )

        try:
            print("=== [CHECKPOINT 2] ATTEMPTING DB USER CREATION ===")
            print(
                "Note: This line automatically calls post_save signals in signals.py right before it finishes!"
            )

            user = AppUser.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name,
                age=age,
                country=country,
                wants_notifications=has_opted_in,
            )
            print("[+] Success: User model successfully written to the database.")

            print("=== [CHECKPOINT 3] ATTEMPTING SESSION BROWSER LOGIN ===")
            login(request, user)
            print("[+] Success: User session registered to browser context.")

            print("=== [CHECKPOINT 4] EVALUATING VIEW EMAIL ROUTINE ===")
            if has_opted_in:
                print(
                    "-> User requested alerts. Triggering View-level send_mail execution..."
                )
                try:
                    subject = "Your First Daily Oasis | Beyond Survival Sisterhood"
                    message = (
                        f"Dearest Sister,\n\n"
                        f"Welcome to your sanctuary. Because you chose to activate daily reminders, "
                        f"here is your structural anchor for today:\n\n"
                        f"📖 BIBLE SCRIPTURE\n"
                        f"\"For I know the plans I have for you,' declares the Lord, 'plans to prosper you "
                        f'and not to harm you, plans to give you hope and a future."\n— Jeremiah 29:11\n\n'
                        f"✨ DAILY AFFIRMATION\n"
                        f'"I am not defined by my anxieties or heavy days. I am deeply loved, securely held, '
                        f'and stepping into my sanctuary step-by-step."\n\n'
                        f"With all our love,\n"
                        f"Beyond Survival Sisterhood Team"
                    )

                    send_mail(
                        subject=subject,
                        message=message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                    )
                    print("[+] Success: View email execution completed safely.")
                except Exception as view_email_err:
                    print(
                        f"[-] Non-Fatal: View send_mail failed internally but caught smoothly: {str(view_email_err)}"
                    )
            else:
                print(
                    "-> User did not request notifications. Skipping View email dispatch."
                )

            print("=== [CHECKPOINT 5] REDIRECTING USER TO DASHBOARD ===\n")
            return redirect("dashboard")

        except Exception as main_error:
            print("\n!!! CRITICAL REGISTRATION CRASH INTERCEPTED !!!")
            print(f"The underlying error class type is: {type(main_error).__name__}")
            print(f"The exact error message is: {str(main_error)}")
            print("-----------------------------------------------------")
            print("FULL PYTHON EXCEPTION TRACE:")
            traceback.print_exc()  # This prints the specific line number where the code broke
            print("-----------------------------------------------------\n")

            return render(
                request,
                "main_app/signup.html",
                {
                    "error": f"Backend Error Code: ({type(main_error).__name__}) - {str(main_error)}",
                    "countries": countries,
                },
            )

    return render(request, "main_app/signup.html", {"countries": countries})


def groups_views(request):
    """Displays active support groups."""
    active_groups = SupportGroup.objects.all()
    return render(request, "main_app/groups.html", {"groups": active_groups})


def login_view(request):
    """Handles user login requests."""
    if request.user.is_authenticated:
        return redirect("dashboard")  # Redirect if they are already signed in

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect("dashboard")  # Send them straight to the workspace
    else:
        form = AuthenticationForm()

    return render(request, "main_app/login.html", {"form": form})
