def get_user_level(done_count: int):
    milestones = [
        {"name": "Initiate", "required": 0, "icon": "🥚"},
        {"name": "Bronze Builder", "required": 10, "icon": "🥉"},
        {"name": "Silver Consistent", "required": 25, "icon": "🥈"},
        {"name": "Gold Finisher", "required": 50, "icon": "🥇"},
        {"name": "Elite Relentless", "required": 100, "icon": "🏆"}
    ]

    current_level = None
    next_milestone = None

    for milestone in milestones:
        if done_count >= milestone["required"]:
            current_level = milestone
        elif not next_milestone:
            next_milestone = milestone

    return current_level