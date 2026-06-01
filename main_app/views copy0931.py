import datetime
import hashlib
import random

import requests
from decouple import config
from django.contrib import messages
from django.contrib.auth import login
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django_countries import countries
from google import genai

from .models import (
    AppUser,  # Ensure this matches the custom user model we created
    DailyUplift,
    GratitudeThought,
    SupportGroup,
)

# Initialize client outside the function to reuse the connection
API_KEY = config("GEMINI_API_KEY", default="")
client = genai.Client(api_key=API_KEY) if API_KEY else None


def get_ai_explanation(prompt_text):
    if not prompt_text or not client:
        return "Take a moment to let this message resonate with your spirit."

    # 1. Generate a unique Cache Key for this specific text
    # This prevents redundant API calls
    text_hash = hashlib.md5(prompt_text.encode()).hexdigest()
    cache_key = f"wellness_ai_{text_hash}"

    # 2. Check Cache first
    cached_res = cache.get(cache_key)
    if cached_res:
        return cached_res

    try:
        # 3. Call Gemini only if not in cache
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                f"Provide a 2-sentence comforting explanation for: {prompt_text}"
            ],
        )

        if response and response.text:
            explanation = response.text.strip()
            # 4. Save to cache for 24 hours
            cache.set(cache_key, explanation, 86400)
            return explanation

    except Exception as e:
        # Log the error to your console so you can see it
        print(f"Gemini API limit reached or error: {e}")
        # Return a fallback message so the user sees something beautiful
        return "Peace begins with a quiet mind. Let this message settle in your heart."

    return "Reflect on how this truth can guide your steps today."


def fetch_explanation(request):
    text_to_explain = request.GET.get("text", "")
    if not text_to_explain:
        return JsonResponse({"explanation": "No text provided."}, status=400)

    # This uses the Caching logic we built earlier
    explanation = get_ai_explanation(text_to_explain)
    return JsonResponse({"explanation": explanation})


def index(request):
    return render(request, "main_app/index.html")


def signup_view(request):
    if request.method == "POST":
        # Extract the data from the form
        name = request.POST.get("name")
        age = request.POST.get("age")
        email = request.POST.get("email")
        country = request.POST.get("country")
        # Checkbox returns 'on' if checked, otherwise None
        notifications = request.POST.get("notifications") == "on"

        # Basic logic to create the user in your database
        try:
            # We use email as the username for uniqueness
            user = AppUser.objects.create_user(
                username=email,
                email=email,
                first_name=name,
                age=age,
                country=country,
                wants_notifications=notifications,
            )
            # Log the user in immediately after signup
            login(request, user)
            return redirect("dashboard")  # Redirect to the day-specific dashboard

        except Exception as e:
            # If there's an error (e.g. email already exists), return to form with error
            return render(
                request,
                "main_app/signup.html",
                {"error": "Email already registered or invalid data."},
            )

    # If it's a GET request, just show the empty signup form
    return render(request, "main_app/signup.html", {"countries": countries})


def dashboard_view_old(request):
    # 1. Handle User Greeting
    if request.user.is_authenticated:
        user_name = request.user.first_name if request.user.first_name else "Mike"
    else:
        user_name = "Guest"

    # 2. Get the Date
    today_full = datetime.datetime.now().strftime("%A").upper()

    # 3. Fetch the Bible Verse (The missing piece)
    api_url = "https://bible-api.com/data/web/random"
    try:
        response = requests.get(api_url, timeout=5)
        data = response.json()
        # Extract from the nested 'random_verse' dictionary
        verse_data = data.get("random_verse", {})
        text = verse_data.get("text", "").strip()
        book = verse_data.get("book", "")
        chapter = verse_data.get("chapter", "")
        verse_num = verse_data.get("verse", "")
        # Format the string properly
        random_verse = f"{text} - {book} {chapter}:{verse_num}"
    except Exception:
        # Fallback if the API is down or slow
        random_verse = "Be still, and know that I am God. - Psalm 46:10"

    try:
        response = requests.get("https://www.affirmations.dev/", timeout=5)
        # Note: This API returns {"affirmation": "Text here"}
        affirmation = response.json().get("affirmation")
        affirmation_explanation = get_ai_explanation(affirmation)
        print(affirmation_explanation)
    except:
        affirmation = "I am strong, capable, and worthy."

    try:
        # Advice Slip API is free and doesn't require a key for basic use
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        wellness_tip = response.json().get("slip", {}).get("advice")
    except Exception:
        wellness_tip = "Take a deep breath and stay present in this moment."

    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        # We use advice as a prompt: "Reflect on this: [Advice]"
        gratitude_prompt = f"What are you thankful for regarding this: {response.json().get('slip', {}).get('advice')}"
    except:
        gratitude_prompt = "What is one small thing that went well today?"

    try:
        # Fetching from a clean, reliable quotes API
        response = requests.get(
            "https://api.quotable.io/random?tags=wisdom|inspirational", timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            daily_intention = data.get("content")
    except:
        daily_intention = (
            "I choose to lead with grace and build my strength one day at a time."
        )

    # 2. Handle Saving a New Thought
    if request.method == "POST" and "save_thought" in request.POST:
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

    # 2. Fetch the list
    previous_thoughts = GratitudeThought.objects.filter(user=request.user).order_by(
        "-created_at"
    )
    # 4. Pass EVERYTHING to the template
    return render(
        request,
        "main_app/dashboard.html",
        {
            "user_name": user_name,
            "today_full": today_full,
            "daily_inspiration": random_verse,
            "inspiration_explanation": get_ai_explanation(random_verse),
            "daily_affirmation": affirmation,
            "affirmation_explanation": get_ai_explanation(affirmation),
            "daily_wellness_tip": wellness_tip,
            "wellness_tip_explanation": get_ai_explanation(wellness_tip),
            "gratitude_prompt": gratitude_prompt,
            "gratitude_prompt_explanation": get_ai_explanation(gratitude_prompt),
            "previous_thoughts": previous_thoughts,
            "daily_intention": daily_intention,
            "daily_intention_explanation": get_ai_explanation(daily_intention),
        },
    )


def dashboard_view(request):
    # 1. Handle User Greeting
    if request.user.is_authenticated:
        user_name = request.user.first_name if request.user.first_name else "Mike"
    else:
        user_name = "Guest"

    today_full = datetime.datetime.now().strftime("%A").upper()

    # 2. THE CACHE WRAPPER: Try to get data from cache first
    # We save this dictionary for 1 hour (3600 seconds)
    cache_key = "daily_dashboard_data"
    data = cache.get(cache_key)

    if not data:
        # If cache is empty, fetch from APIs

        # BIBLE VERSE
        try:
            res = requests.get("https://bible-api.com/data/web/random", timeout=3)
            v = res.json().get("random_verse", {})
            random_verse = f"{v.get('text', '').strip()} - {v.get('book')} {v.get('chapter')}:{v.get('verse')}"
        except:
            random_verse = "Be still, and know that I am God. - Psalm 46:10"

        # AFFIRMATION
        try:
            res = requests.get("https://www.affirmations.dev/", timeout=3)
            affirmation = res.json().get("affirmation")
        except:
            affirmation = "I am strong, capable, and worthy."

        # WELLNESS & GRATITUDE
        try:
            res = requests.get("https://api.adviceslip.com/advice", timeout=3)
            advice = res.json().get("slip", {}).get("advice")
            wellness_tip = advice
            gratitude_prompt = f"What are you thankful for regarding this: {advice}"
        except:
            wellness_tip = "Take a deep breath and stay present."
            gratitude_prompt = "What is one small thing that went well today?"

        # INTENTION
        try:
            # Note: quotable.io is often down, added a quick timeout
            res = requests.get("https://api.quotable.io/random?tags=wisdom", timeout=3)
            daily_intention = res.json().get("content")
        except:
            daily_intention = "I choose to lead with grace and build strength."

        data = {
            "daily_inspiration": random_verse,
            "daily_affirmation": affirmation,
            "daily_wellness_tip": wellness_tip,
            "gratitude_prompt": gratitude_prompt,
            "daily_intention": daily_intention,
        }

        # Store in cache so the NEXT 1,000 refreshes are instant
        cache.set(cache_key, data, 3600)

    # 3. Handle POST (Remains the same)
    if request.method == "POST" and "save_thought" in request.POST:
        thought_text = request.POST.get("thought")
        active_prompt = request.POST.get("active_prompt")
        if thought_text and request.user.is_authenticated:
            GratitudeThought.objects.create(
                user=request.user, prompt=active_prompt, thought=thought_text
            )
            messages.success(request, "Your reflection has been saved.")
            return redirect("dashboard")

    # 4. Final Context
    context = {
        "user_name": user_name,
        "today_full": today_full,
        "previous_thoughts": GratitudeThought.objects.filter(
            user=request.user
        ).order_by("-created_at")
        if request.user.is_authenticated
        else [],
    }
    context.update(data)  # Merge the API data into context

    return render(request, "main_app/dashboard.html", context)


def groups_view(request):
    # This pulls REAL data entered in your admin panel
    active_groups = SupportGroup.objects.all()

    return render(request, "main_app/groups.html", {"groups": active_groups})


def chatbot_response(request):
    mood = request.GET.get("mood")
    # Get today's content for relevant quotes/mantras
    today_content = DailyUplift.objects.filter(
        day_of_week=datetime.date.today().weekday()
    ).first()

    response_data = {
        "anxious": {
            "message": "Take a deep breath. You are capable and strong.",
            "scripture": "Philippians 4:6-7",  # As requested in the audio
            "action": "Try this 4-7-8 breathing exercise.",
        },
        "sad": {
            "message": "It's okay to not be okay. Your feelings are valid.",
            "scripture": "Psalm 34:18",
            "action": "Reach out to one of our support groups below.",
        },
        "lonely": {
            "message": "You are not alone in this journey.",
            "scripture": "Matthew 28:20",
            "action": "Join our community discussion board.",
        },
    }

    selected_response = response_data.get(
        mood, {"message": "How can I support you today?"}
    )

    return render(
        request,
        "main_app/chatbot_partial.html",
        {"response": selected_response, "today": today_content},
    )


def bible_verse_view(request):
    # API endpoint for a random verse
    api_url = "https://bible-api.com/data/web/random"

    try:
        response = requests.get(api_url)
        data = response.json()
        # Format the text with the reference (e.g., "John 3:16")
        random_verse = f"{data['text'].strip()} - {data['reference']}"
    except:
        # Fallback in case of no internet
        random_verse = "Be still, and know that I am God. - Psalm 46:10"

    return render(
        request,
        "main_app/dashboard.html",
        {
            "daily_inspiration": random_verse,
            "user_name": request.user.first_name
            if request.user.is_authenticated
            else "Mike",
            "today_full": datetime.datetime.now().strftime("%A").upper(),
        },
    )


def get_affirmation():
    try:
        print("daily affirm")
        response = requests.get("https://www.affirmations.dev/", timeout=5)
        print(response)
        # Note: This API returns {"affirmation": "Text here"}
        return response.json().get("affirmation")
    except:
        print("ERROR daily affirm")
        return "I am strong, capable, and worthy."
