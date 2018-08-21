
from pydub import AudioSegment
import os

def audio_folder_split(segment_len, audio_folder, msg=True):
    files = os.listdir(audio_folder)
    splitdir = "split_audios"

    # Adds numbers to titles if split_audio folder already exists
    if splitdir in files:
        i = 1
        splitdir += str(i)
        while splitdir in files:
            splitdir = splitdir[:-1] + str(i)
            i+=1
    os.mkdir(audio_folder + "/" + splitdir)

    # Loops through each .wav audio file
    for file in files:
        if file[-4:].lower() != '.wav':
            continue
        file_path = audio_folder + "/" + file
        sound = AudioSegment.from_file(file_path)
        size = len(sound)
        nsegs = int(size / segment_len) + (size % segment_len > 0)

        # Just to prevent accidentally creating 100+ files
        if nsegs > 100 and msg:
            print('File "{}" will make {} files, skip this one? (y/n)'.format(file, nsegs))
            if input().lower() in ('y', 'yes'):
                continue

        newdir = audio_folder + "/" + splitdir + "/" + file[:-4] + "/"
        os.mkdir(newdir)

        # Splits the files into equal length segments
        for x in range(nsegs):
            seg_sound = sound[x * segment_len:(x + 1) * segment_len]
            path = newdir + file[:-4] + "_split" + str(x) + ".wav"
            seg_sound.export(path, format="wav")
    print("Files successfully split into {} folder!".format(splitdir))

# loc = '/Users/jeremy.meyer/Desktop/wyze_camera/audio'

print("How long do you want each audio segment? (milliseconds)")
while True:
    try:
        seg_len = int(input())
        if seg_len > 0:
            break
        else:
            print("Please provide a positive integer!")
    except TypeError:
        print("Please provide an integer!")

print("Location of the folder with all audio files? (Will split all .wav files in folder)")
loc = input()
audio_folder_split(seg_len, loc)
