#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gtts import gTTS
import os
import urllib3

urllib3.disable_warnings()
tts = gTTS(text='테스트', lang='ko')
tts.save("tts.mp3")
os.system("mpg321 tts.mp3")
