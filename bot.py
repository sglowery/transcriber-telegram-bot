import json
import os

import speech_recognition as sr
from pydub import AudioSegment
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext.filters import Filters

GROUP_TOGGLES_PATH = "group-toggles.json"


def main(args):
    run(args[1])


def run(token):
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("toggle", toggle_group_auto_transcribe))
    updater.dispatcher.add_handler(CommandHandler("transcribe", transcribe_from_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, transcribe_from_message))
    updater.dispatcher.add_handler(CommandHandler("status", get_auto_transcription_status))
    updater.dispatcher.add_error_handler(on_error)
    print('Started')
    updater.start_polling()


def toggle_group_auto_transcribe(update, context):
    ensure_group_toggles_file()
    group_id = str(update.message.chat.id)
    with open(GROUP_TOGGLES_PATH, 'r') as f:
        group_toggles = json.load(f)
    current_group_toggle = group_toggles.get(group_id, True)
    group_toggles.update({group_id: not current_group_toggle})
    with open(GROUP_TOGGLES_PATH, 'w') as f:
        json.dump(group_toggles, f, indent=2)
    response = f"Auto-transcription is now {'disabled' if current_group_toggle else 'enabled'}"
    update.message.reply_text(response)


def get_auto_transcription_status(update, context):
    ensure_group_toggles_file()
    with open(GROUP_TOGGLES_PATH) as f:
        group_status = json.load(f).get(str(update.message.chat.id))
        update.message.reply_text(f"Auto-transcription is currently {'enabled' if group_status else 'disabled'}")


def transcribe_from_message(update, context):
    message = update.message
    group_id = message.chat.id
    if is_auto_transcribe(group_id):
        text = transcribe_voice(message)
        context.bot.send_message(group_id, text, reply_to_message_id=message.message_id)


def transcribe_from_command(update, context):
    message = update.message
    reply_to_message = message.reply_to_message
    text = transcribe_voice(reply_to_message)
    context.bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)


def transcribe_voice(message):
    voice = message.voice
    if voice:
        tfile = voice.get_file(timeout=10)
        path = tfile.download()
        text = transcribe_file(path)
        os.remove(path)
        return text


def transcribe_file(path):
    new_path = 'file.wav'
    AudioSegment.from_ogg(path).export(new_path, format='wav')

    r = sr.Recognizer()
    with sr.AudioFile(new_path) as source:
        audio = r.record(source)
    os.remove(new_path)

    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        return '<could not understand audio>'


def is_auto_transcribe(group_id):
    ensure_group_toggles_file()
    with open(GROUP_TOGGLES_PATH, 'r') as f:
        return json.load(f).get(str(group_id), True)


def ensure_group_toggles_file():
    try:
        with open(GROUP_TOGGLES_PATH, 'r') as f:
            pass
    except FileNotFoundError:
        with open(GROUP_TOGGLES_PATH, 'x+') as f:
            json.dump({}, f, indent=2)


def on_error(update, context):
    print(context.error)
    context.bot.send_message(update.message.chat.id, '<an error occurred>',
                             reply_to_message_id=update.message.message_id)


if __name__ == '__main__':
    import sys

    main(sys.argv)
