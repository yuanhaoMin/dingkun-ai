import openai, os



audio_file= open("../resources/test_regist.m4a", "rb")
transcript = openai.Audio.transcribe("whisper-1", audio_file)
print(transcript['text'])
