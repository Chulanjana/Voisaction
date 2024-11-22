import os
from pydub import AudioSegment

def extract_five_second_clips(input_wav_path, start_time_ms, end_time_ms, speaker_tag, speaker_clips_count):
    audio = AudioSegment.from_file(input_wav_path)
    output_files = []

    # Ensure start extraction only if less than 10 clips have been extracted for this speaker
    if speaker_clips_count.get(speaker_tag, 0) >= 10:
        print(f"Already extracted 10 clips for {speaker_tag}. Skipping further extraction.")
        return output_files

    # Start extracting 5-second clips within the specified time range
    clip_start_time = start_time_ms * 1000  # Convert start time to milliseconds
    while clip_start_time < end_time_ms * 1000:
        clip_end_time = clip_start_time + 5000  # Define end time for a 5-second clip

        # Ensure we don't exceed the end_time_ms and skip clips shorter than 5 seconds
        if clip_end_time > end_time_ms * 1000 or (clip_end_time - clip_start_time) < 4000:
            break

        # Skip extraction if we've already reached 10 clips for this speaker tag
        current_clip_count = speaker_clips_count.get(speaker_tag, 0)
        if current_clip_count >= 10:
            break

        # Extract and export the 5-second clip
        clip = audio[clip_start_time:clip_end_time]
        base_name = os.path.splitext(input_wav_path)[0]
        clip_index = current_clip_count + 1  # Next clip index for this speaker
        clip_path = f"{base_name}_{speaker_tag}_clip_{clip_index}.wav"
        
        clip.export(clip_path, format="wav")
        print(f"Saved 5-second clip to {clip_path}")
        output_files.append(clip_path)

        # Update the clip count for this speaker tag
        speaker_clips_count[speaker_tag] = clip_index

        # Move to the next 5-second segment
        clip_start_time += 5000

    return output_files



# https://www.figma.com/design/c5TQKiZ1ltp5wqifb6cSl1/ML-project?node-id=0-1&node-type=canvas&t=UISIVKfH0X4EV2ai-0