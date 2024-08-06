import subprocess
import sys
import pandas as pd
def extract_clips(f):
    df = pd.read_csv(f,header=None,comment="#",sep="\t")
    df = df.dropna()
    count = 0
    for i,r in df.iterrows():
        count += 1
        input_file = r[0]
        start_time, end_time = r[1],r[2]
        output_clip = f'clip_{count}.mp4'
        start_frame = time_to_frame(start_time)
        end_frame = time_to_frame(end_time)
        duration_frames = end_frame - start_frame

        command = [
            'ffmpeg', '-i', input_file, '-vf',
            f'select=between(n\\,{start_frame}\\,{end_frame}),setpts=PTS-STARTPTS',
            '-vsync', 'vfr', '-af', f'aselect=between(n\\,{start_frame}\\,{end_frame}),asetpts=PTS-STARTPTS',
            output_clip, '-hide_banner', '-loglevel', 'error'
        ]
        # command = [
        #     'ffmpeg', '-i', input_file, '-ss', start_time, '-t', "2",
        #     '-c', 'copy', output_clip, '-hide_banner', '-loglevel', 'error'
        # ]
        subprocess.run(command)

        # Add clip to list for concatenation
        with open('clips.txt', 'a') as clip_file:
            clip_file.write(f"file '{output_clip}'\n")

def merge_clips(output_file):
    command = [
        'ffmpeg', '-f', 'concat', '-safe', '0', '-i', 'clips.txt', '-c', 'copy', output_file
    ]
    subprocess.run(command)

def clean_up():
    subprocess.run(['rm', 'clip_*.mp4', 'clips.txt'])
def time_to_frame(time_str, fps=30):
    parts = list(map(float, time_str.split(':')))
    if len(parts) == 2:
        m, s = parts
        h = 0
    elif len(parts) == 1:
        s = parts[0]
        h = m = 0
    else:
        h, m, s = parts
    total_seconds = h * 3600 + m * 60 + s
    return int(total_seconds * fps)

extract_clips(sys.argv[1])
merge_clips(sys.argv[2])
clean_up()

