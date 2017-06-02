from gtts import gTTS
import os
tts = gTTS(text='테스트', lang='ko')
tts.save("tts.mp3")
os.system("mpg321 tts.mp3")
