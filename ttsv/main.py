import argparse
from ttsv.process_file import process_input_texts
from ttsv.merge import create_merge_files
from ttsv.generate_video import create_black_videos_with_audio
from ttsv.youtube_upload import upload_video_to_channels

def main():
    parser = argparse.ArgumentParser(description="Run the TTS video generation pipeline.")
    parser.add_argument("--step", type=int, choices=range(0, 5), 
                        help="Run only a specific step (0-4).")
    parser.add_argument("--from-step", type=int, choices=range(0, 5), 
                        help="Run from a specific step onward (0-4).")

    args = parser.parse_args()

    if args.step is not None and args.from_step is not None:
        print("Error: You cannot specify both --step and --from-step at the same time.")
        return

    # Step functions
    def step_0():
        from ttsv.model import ZonosTTS
        print("[Step 0] Initializing model...")
        return ZonosTTS(model_path="Zyphra/Zonos-v0.1-transformer",
                        reference_audio_path="assets/exampleaudio.mp3")

    def step_1(model):
        print("[Step 1] Processing input texts...")
        process_input_texts(input_dir="text_input", filename="Test", model=model)

    def step_2():
        print("[Step 2] Merging output files...")
        create_merge_files()

    def step_3():
        print("[Step 3] Generating black video with audio...")
        create_black_videos_with_audio()

    def step_4():
        print("[Step 4] Uploading video to YouTube...")
        upload_video_to_channels()

    # Handling the step logic
    steps = {
        0: step_0,
        1: step_1,  # Requires model
        2: step_2,
        3: step_3,
        4: step_4
    }

    # Run a single step if --step is provided
    if args.step is not None:
        if args.step == 1:
            model = step_0()  # Initialize model before step 1
            step_1(model)
        else:
            steps[args.step]()  # Run only the requested step
        return

    # Run from a specific step onward
    start_step = args.from_step if args.from_step is not None else 0

    model = None
    if start_step == 0 or start_step == 1:
        model = step_0()

    for step in range(start_step, 5):
        if step == 1:
            step_1(model)
        else:
            steps[step]()

if __name__ == "__main__":
    main()
