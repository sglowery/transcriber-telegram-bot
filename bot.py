import os
import speech_recognition as sr
from pydub import AudioSegment
from telegram import TelegramError
from telegram.ext import MessageHandler, Updater
from telegram.ext.filters import Filters


def main(args):
    run(args[1])


def run(token):
    updater = Updater(token, use_context=True)
    updater.dispatcher.add_handler(MessageHandler(Filters.voice, on_voice_message))
    updater.dispatcher.add_error_handler(on_error)
    print('Started')
    updater.start_polling()


def on_voice_message(update, context):
    message = update.message
    if message:
        voice = message.voice
        if voice:
            tfile = voice.get_file(timeout=10)
            path = tfile.download()
            text = transcribe_file(path)
            os.remove(path)
            context.bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)


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


def on_error(update, context):
    print(context.error)
    context.bot.send_message(update.message.chat.id, '<an error occurred>',
        reply_to_message_id=update.message.message_id)


if __name__ == '__main__':
    import sys
    main(sys.argv)
