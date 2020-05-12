#!/usr/bin/env python

from distutils.core import setup

setup(
    name='transcriber-telegram-bot',
    version='1.0',
    description='Telegram bot to transcribe voice messages',
    author='Nick Lowery',
    license='MIT',
    url='https://github.com/ClockVapor/transcriber-telegram-bot',
    install_requires=['pydub', 'python-telegram-bot', 'SpeechRecognition'],
)
