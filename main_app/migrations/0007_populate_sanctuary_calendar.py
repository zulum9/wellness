# main_app/migrations/0007_populate_sanctuary_calendar.py
from django.db import migrations


def populate_calendar_content(apps, schema_editor):
    DailySanctuaryContent = apps.get_model("main_app", "DailySanctuaryContent")

    # The blueprint repeats structurally each week across 30 days
    content_map = {
        "identity": {
            "divine_guidance": "Before I formed you in the womb I knew you. - Jeremiah 1:5",
            "daily_affirmation": "I am known. I am chosen. I am not an accident. My name was written before I took my first breath. I am enough, exactly as I am.",
            "wellness_tip": "Write down 3 words that describe YOU - not your roles, not what you do for others, just you. This simple exercise reconnects you to your core identity and is one of the most powerful tools in building unshakeable self-worth.",
            "gratitude_prompt": "What is one thing about who you are grateful for today? Your personality, your strength, your story that you are.",
            "daily_intention": "I choose to reject every label the world placed on me that God never gave me.",
        },
        "confidence": {
            "divine_guidance": "I can do all things through Christ who strengthens me. - Philippians 4:13",
            "daily_affirmation": "I am capable. I am qualified. I do not need to shrink to make others comfortable. My voice matters, my ideas matter, and I take up space unapologetically.",
            "wellness_tip": "Before you walk into any room today, take 3 slow deep breaths and stand tall. Research shows that posture directly impacts how confident we feel. Your body language speaks to your mind before it speaks to anyone else so stand like you belong, because you do.",
            "gratitude_prompt": "What is one achievement big or small that proves to you that you are more capable than you give yourself credit for?",
            "daily_intention": "I choose to do the thing that scares me, knowing that courage is a muscle I am building every single day.",
        },
        "healing": {
            "divine_guidance": "He heals the brokenhearted and binds up their wounds. - Psalm 147:3",
            "daily_affirmation": "I am healing. I am not defined by what was done to me or what I have been through. I give myself permission to let go, to grieve, and to grow. My past does not own my future.",
            "wellness_tip": "Try this tonight: write down one thing that has been weighing on your heart - then fold the paper and place it aside. This act of externalising your pain is a technique used in therapy to create emotional distance from difficult feelings. You don't have to solve it today. Sometimes acknowledging it is enough.",
            "gratitude_prompt": "What is one hard season in your life that, looking back, made you stronger or taught you something valuable?",
            "daily_intention": "I choose healing over hiding. I choose to be gentle with myself today.",
        },
        "purpose": {
            "divine_guidance": "For we are God's handiwork, created in Christ Jesus to do good works, which God prepared in advance for us to do. - Ephesians 2:10",
            "daily_affirmation": "I am purposeful. Everything I have been through, every struggle, every detour, every lesson has been preparing me for exactly where I am going. I will not despise my process.",
            "wellness_tip": "Ask yourself this powerful question today: 'What would I do even if I wasn't paid for it?' Purpose often lives at the intersection of your passion, your pain, and the problems you feel called to solve. Your answer might surprise you.",
            "gratitude_prompt": "What is one gift, talent, or quality you have that you could use to make someone else's life better?",
            "daily_intention": "I choose to take one small step today toward the life I know I was created to live.",
        },
        "abundance": {
            "divine_guidance": "The Lord is my shepherd, I lack nothing. - Psalm 23:1",
            "daily_affirmation": "I am worthy of good things. I release the belief that I must suffer to deserve blessings. Opportunities find me. Favour follows me. I walk in abundance - spirit, mind, and body.",
            "wellness_tip": "Practice a scarcity detox today. Every time a thought like 'I'll never have enough' comes up, replace it with 'something good is on its way.' This is not blind positivity - it's rewiring a thought pattern that may be keeping you stuck. Our brains believe what we repeatedly tell them.",
            "gratitude_prompt": "List 3 ways you are already abundant today - things, people, or moments that are evidence that you are blessed.",
            "daily_intention": "I choose to celebrate every small win today, knowing that gratitude opens the door for more.",
        },
        "sisterhood": {
            "divine_guidance": "Two are better than one, because they have a good return for their labor. - Ecclesiastes 4:9",
            "daily_affirmation": "I am surrounded by women who want to see me win. I am not in competition, I am in community. I celebrate others freely because I know there is enough room for all of us to shine.",
            "wellness_tip": "Reach out to one woman in your life today - a friend, a sister, a mentor - just to check in. Studies consistently show that meaningful social connection is one of the strongest predictors of mental wellness. A simple 'I was thinking of you' can change someone's entire day. Including yours.",
            "gratitude_prompt": "Who is a woman in your life who has poured into you, believed in you, or simply shown up for you? Take a moment to be grateful for her today.",
            "daily_intention": "I choose to be the kind of woman who lifts other women. I choose sisterhood over silence.",
        },
        "rest_faith": {
            "divine_guidance": "Come to me, all you who are weary and burdened, and I will give you rest. - Matthew 11:28",
            "daily_affirmation": "I am held. Even on the days I feel like I am falling apart, I am held by hands greater than my own. I do not have to have it all figured out. I release control and choose faith over fear.",
            "wellness_tip": "Today, give yourself full permission to rest without guilt. Put your phone down for at least one hour. Go outside, pray, journal, nap, or simply be still. Rest is productive. Your nervous system needs it. You cannot pour from an empty cup, and refilling is not optional - it is essential.",
            "gratitude_prompt": "Reflect on this past week - what is one moment, breakthrough, or lesson you are carrying into next week with gratitude?",
            "daily_intention": "I choose to be still. I choose to trust. I choose to rest in the knowledge that God is working even when I cannot see it.",
        },
    }

    theme_sequence = [
        "identity",
        "confidence",
        "healing",
        "purpose",
        "abundance",
        "sisterhood",
        "rest_faith",
    ]

    for day in range(1, 31):
        index = (day - 1) % 7
        selected_theme = theme_sequence[index]
        data = content_map[selected_theme]

        DailySanctuaryContent.objects.create(
            day_number=day,
            divine_guidance=data["divine_guidance"],
            daily_affirmation=data["daily_affirmation"],
            wellness_tip=data["wellness_tip"],
            gratitude_prompt=data["gratitude_prompt"],
            daily_intention=data["daily_intention"],
        )


def rollback_calendar_content(apps, schema_editor):
    DailySanctuaryContent = apps.get_model("main_app", "DailySanctuaryContent")
    DailySanctuaryContent.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        # Explicitly targets the true current leaf node to keep the graph perfectly linear
        ("main_app", "0006_dailysanctuarycontent_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_calendar_content, rollback_calendar_content),
    ]
