from exam_patterns import DAILY_TEST_SCHEDULE


def get_daily_schedule():
    return DAILY_TEST_SCHEDULE


def format_schedule_message():
    schedule = get_daily_schedule()

    msg = "📅 Daily Auto Test Schedule\n\n"

    for exam, time_slot in schedule:
        msg += f"📝 {exam} → {time_slot}\n"

    return msg
