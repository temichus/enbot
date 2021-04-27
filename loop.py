#!/usr/bin/env python3
import logging
import os
from telepot.loop import MessageLoop
from sqlitedict import SqliteDict
from common_vars import bot, sql_path, name_key, jira_status_key

unexpected_command_str = "Unexpected command. Sorry I can't help you"
already_registered_str = "You are already registered"
done_str = "Done"
pong_str = "Pong"
thanks_str = "Thank you"
not_registered_str = "You are not registered"
help_message = """
/register_me - register you to notification receivers list.
/unregister_me - unregister you from notification receivers list.
/done - mark JIRA is filled.
/ping - check is bot alive.
"""
start_message = "Hello, I can remind you to fill JIRA every Friday.\nType /help to call hint."


logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(os.path.join("var", "log", "register.log"), encoding="utf-8")
logger.addHandler(file_handler)


def send_message(*args, **kwargs):
    try:
        bot.sendMessage(*args, **kwargs)
    except Exception as e:
        logger.error(e)


def start(msg):
    chat_id = msg["chat"]["id"]
    send_message(chat_id, start_message)


def unexpected_command(msg):
    text = msg.get("text", "")
    logger.warning("unexpected command: {}".format(text))
    bot.sendMessage(msg["chat"]["id"], unexpected_command_str)


def register(msg):
    from_id = msg["from"]["id"]
    chat_id = msg["chat"]["id"]
    with SqliteDict(sql_path, autocommit=True) as db:
        if db.get(from_id, None) is not None:
            send_message(chat_id, already_registered_str)
        else:
            db[from_id] = {name_key: msg["from"]["first_name"],
                           jira_status_key: 0}
            send_message(chat_id, "Done")


def unregister(msg):
    from_id = msg["from"]["id"]
    chat_id = msg["chat"]["id"]
    with SqliteDict(sql_path, autocommit=True) as db:
        if db.get(from_id, None) is not None:
            db.pop(from_id)
            send_message(chat_id, done_str)
        else:
            send_message(chat_id, not_registered_str)


def done(msg):
    from_id = msg["from"]["id"]
    chat_id = msg["chat"]["id"]
    with SqliteDict(sql_path, autocommit=True) as db:
        if db.get(from_id, None) is not None:
            db[from_id] = {name_key: msg["from"]["first_name"],
                           jira_status_key: 1}
            send_message(chat_id, thanks_str)
        else:
            send_message(chat_id, not_registered_str)


def ping(msg):
    chat_id = msg["chat"]["id"]
    send_message(chat_id, pong_str)


def help_(msg):
    chat_id = msg["chat"]["id"]
    send_message(chat_id, help_message)


commands = {
    r"/register_me": register,
    r"/unregister_me": unregister,
    r"/done": done,
    r"/ping": ping,
    r"/help": help_,
    r"/start": start,
}


def handle(msg):
    commands.get(msg.get("text", "default"), unexpected_command)(msg)


MessageLoop(bot, handle).run_forever()
