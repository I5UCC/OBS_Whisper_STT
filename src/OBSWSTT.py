import os
import speech_recognition as sr
import whisper
import torch
import sys
import json
from queue import Queue
from time import sleep, time
import numpy as np
import obsws_python as obs


def get_absolute_path(relative_path):
    """Gets absolute path from relative path"""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def clear_screen():
    """Clears the screen"""
    os.system('cls' if os.name=='nt' else 'clear')


def main():
    CONFIG_PATH = get_absolute_path('config.json')
    CONFIG = json.load(open(CONFIG_PATH))

    phrase_time = None
    last_sample = bytes()
    data_queue = Queue()
    recorder = sr.Recognizer()
    recorder.dynamic_energy_threshold = False
    record_timeout = CONFIG["record_timeout"]
    phrase_timeout = CONFIG["phrase_timeout"]
    clear_timeout = CONFIG["clear_timeout"]
    model = CONFIG["model"]
    language = CONFIG["language"]
    energy_threshold = CONFIG["energy_threshold"]
    source_name = CONFIG["source_name"]
    obs_client = obs.ReqClient(host=CONFIG["socket_host"], port=CONFIG["socket_port"], password=CONFIG["socket_password"])
    
    obs_client.set_input_settings(source_name, {'text': ''}, True)

    source = sr.Microphone(sample_rate=16000, device_index=int(CONFIG['microphone_index']) if CONFIG['microphone_index'] else None)

    if model != "large" and language.lower() == "english":
        model = model + ".en"
    device = "cpu" if bool(CONFIG["use_cpu"]) or not torch.cuda.is_available() else "cuda"
    print("Using Device: " + device)
    model = whisper.load_model(model, device=device, download_root=get_absolute_path("whisper_cache/"))
    print("Model loaded.")
    print("Testing Settings...")
    model.transcribe(torch.zeros(256), fp16=torch.cuda.is_available(), language=language, without_timestamps=True)

    cleared = True
    phrase_end = True

    def record_callback(_, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        data_queue.put(data)

    if not energy_threshold:
        print("Adjusting for ambient noise. Please wait a moment and be silent.")
        with source:
            recorder.adjust_for_ambient_noise(source, 3)
            recorder.energy_threshold = round(recorder.energy_threshold, 0) + 30
            print("Threshold: " + str(recorder.energy_threshold))
    else:
        recorder.energy_threshold = energy_threshold

    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    print("Listening...")
    while True:
        try:
            time_last = time()

            if not data_queue.empty():
                cleared = False
                phrase_end = False

                while not data_queue.empty():
                    data = data_queue.get()
                    last_sample += data

                torch_audio = torch.from_numpy(np.frombuffer(last_sample, np.int16).flatten().astype(np.float32) / 32768.0)

                options = {"without_timestamps": True}
                result = model.transcribe(torch_audio, fp16=torch.cuda.is_available(), language=language, **options)
                text = result['text'].strip()

                clear_screen()
                print(text)
                obs_client.set_input_settings(source_name, {'text': text}, True)

                phrase_time = time()
            elif not cleared and phrase_time and time_last - phrase_time > clear_timeout:
                cleared = True
                clear_screen()
                obs_client.set_input_settings(source_name, {'text': ''}, True)
            elif not phrase_end and phrase_time and time_last - phrase_time > phrase_timeout:
                phrase_end = True
                last_sample = bytes()

            sleep(0.1)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
