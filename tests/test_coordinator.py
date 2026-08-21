from nanobot.agents.coordinator import NanobotCoordinator

def test_coordinator_fast_path():
    bot = NanobotCoordinator()
    res = bot.process_message("hi", user_id=1449852069)
    assert res["status"] == "success"
    assert "🐈" in res["response"]

def test_coordinator_unauthorized():
    bot = NanobotCoordinator()
    res = bot.process_message("hi", user_id=12345)
    assert res["status"] == "error"
