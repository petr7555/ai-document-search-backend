import pytest

from ai_document_search_backend.container import Container
from ai_document_search_backend.database_providers.conversation_database import (
    Conversation,
    Message,
    Source,
)

test_username = "test_user"
user_message = Message(role="user", text="Hello")
bot_message = Message(
    role="bot",
    text="Hi",
    sources=[
        Source(
            isin="NO1111111111",
            shortname="Bond 2021",
            link="https://www.example.com/bond1.pdf",
            page=1,
            certainty=0.9,
            distance=0.1,
        ),
        Source(
            isin="NO2222222222",
            shortname="Bond 2022",
            link="https://www.example.com/bond2.pdf",
            page=5,
            certainty=0.8,
            distance=0.2,
        ),
    ],
)

container = Container()
container.config.cosmos.db_name.from_value("TestDB")
db = container.conversation_database()


@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    db.clear_conversations(test_username)
    yield


def test_get_latest_conversation_returns_none_when_conversation_does_not_exist():
    assert db.get_latest_conversation(test_username) is None


def test_adds_a_conversation_with_no_messages():
    conversation = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    db.add_conversation(test_username, conversation)
    assert db.get_latest_conversation(test_username) == conversation


def test_adds_a_conversation_with_messages():
    conversation = Conversation(
        created_at="2021-01-01T00:00:00", messages=[user_message, bot_message]
    )
    db.add_conversation(test_username, conversation)
    assert db.get_latest_conversation(test_username) == conversation


def test_gets_latest_conversation_with_no_messages():
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(created_at="2021-01-02T00:00:00", messages=[])
    db.add_conversation(test_username, conversation_newer)
    db.add_conversation(test_username, conversation_older)
    assert db.get_latest_conversation(test_username) == conversation_newer


def test_gets_latest_conversation_with_messages():
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(
        created_at="2021-01-02T00:00:00", messages=[user_message, bot_message]
    )
    db.add_conversation(test_username, conversation_newer)
    db.add_conversation(test_username, conversation_older)
    assert db.get_latest_conversation(test_username) == conversation_newer


def test_adds_to_latest_conversation_with_no_messages():
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(created_at="2021-01-02T00:00:00", messages=[])
    db.add_conversation(test_username, conversation_newer)
    db.add_conversation(test_username, conversation_older)
    db.add_to_latest_conversation(test_username, user_message, bot_message)

    assert db.get_latest_conversation(test_username) == Conversation(
        created_at="2021-01-02T00:00:00", messages=[user_message, bot_message]
    )


def test_adds_to_latest_conversation_with_existing_messages():
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(
        created_at="2021-01-02T00:00:00", messages=[user_message, bot_message]
    )
    db.add_conversation(test_username, conversation_newer)
    db.add_conversation(test_username, conversation_older)
    db.add_to_latest_conversation(test_username, user_message, bot_message)

    assert db.get_latest_conversation(test_username) == Conversation(
        created_at="2021-01-02T00:00:00",
        messages=[user_message, bot_message, user_message, bot_message],
    )


def test_raises_error_when_adding_messages_without_any_existing_conversation():
    try:
        db.add_to_latest_conversation(test_username, user_message, bot_message)
        assert False
    except ValueError as e:
        assert str(e) == "No conversation found for user test_user"


def test_clears_conversations():
    conversation_older = Conversation(created_at="2021-01-01T00:00:00", messages=[])
    conversation_newer = Conversation(created_at="2021-01-02T00:00:00", messages=[])
    db.add_conversation(test_username, conversation_newer)
    db.add_conversation(test_username, conversation_older)
    db.clear_conversations(test_username)
    assert db.get_latest_conversation(test_username) is None
