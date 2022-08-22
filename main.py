import time

from helpers import print_progressBar
from threading import Thread, Lock
from googletrans import Translator

srt_path = "E:\\en-house.of.the.dragon.s01e01.srt"
dest_path = "E:\\house.of.the.dragon.s01e01.srt"
delay_milli_seconds = -1000

f = open(srt_path, encoding="utf-8")
lines_raw = f.read().split('\n\n')
lines = []
for line_raw in lines_raw:
    if len(line_raw.split('\n')) > 2:
        lines.append(line_raw)

f.close()

max_line_index = len(lines)
line_done_numer = 0


def translate_line(line_index, lock):
    global lines
    global line_done_numer

    try:
        line = lines[line_index]
        line_split = line.split('\n')
        time_define_arr = line_split[1].split(' --> ')
        from_time_milli_seconds = time_str_to_milli_seconds(time_define_arr[0])
        to_time_milli_seconds = time_str_to_milli_seconds(time_define_arr[1])
        line_split[1] = ' --> '.join([time_milli_seconds_to_str(from_time_milli_seconds + delay_milli_seconds),
                                      time_milli_seconds_to_str(to_time_milli_seconds + delay_milli_seconds)])

        target_text = line_split[0:2]
        translated_text = Translator().translate('\n'.join(line_split[2:]), src='en', dest='vi').text
        target_text.append(translated_text)
        lines[line_index] = '\n'.join(target_text)
        lock.acquire()
        line_done_numer += 1
        print_progressBar(line_done_numer, max_line_index, prefix='Progress:', suffix='Complete', length=100)
        lock.release()
    except Exception as e:
        print(str(e))
        translate_line(line_index, lock)


def time_str_to_milli_seconds(time_str):
    time_str = time_str.replace(',', '.')
    time_arr = time_str.split(':')
    time_seconds = float(time_arr[0]) * 60 * 60 + float(time_arr[1]) * 60 + float(time_arr[2])
    return time_seconds * 1000


def time_milli_seconds_to_str(time_milli_seconds):
    time_milli_seconds = int(time_milli_seconds)
    time_seconds = int(time_milli_seconds / 1000)
    hours = int(time_seconds / 3600)
    minutes = int((time_seconds % 3600) / 60)
    seconds = int(time_seconds % 60)
    milli_seconds = int(time_milli_seconds % 1000)

    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f},{milli_seconds:03.0f}"


if __name__ == "__main__":
    print_progressBar(0, max_line_index, prefix='Progress:', suffix='Complete', length=100)
    threads = []
    lock = Lock()

    for index in range(max_line_index):
        thread = Thread(target=translate_line, args=(index, lock))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    f = open(dest_path, 'w', encoding="utf-8")
    f.write('\n\n'.join(lines))
    f.close()
