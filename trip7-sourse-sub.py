import azure.cognitiveservices.speech as speechsdk
from datetime import datetime, timedelta


def format_time(nanoseconds):
    """
    Format time for SRT subtitle from Azure's 100-nanosecond units
    Azure 的 audio_offset 是 100纳秒为单位
    需要转换为 HH:MM:SS,mmm 格式
    """
    # 转换为秒
    total_seconds = nanoseconds / 10000000  # 100纳秒转秒

    # 计算时分秒毫秒
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    milliseconds = int((total_seconds * 1000) % 1000)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def create_srt(word_boundaries, output_path):
    """Generate SRT subtitle file"""
    with open(output_path, "w", encoding="utf-8") as srt_file:
        subtitle_index = 1
        current_line = []
        current_start = None

        for i, word in enumerate(word_boundaries):
            if current_start is None:
                current_start = word["audio_offset"]

            current_line.append(word["text"])

            # Convert duration from timedelta to microseconds
            duration_microseconds = int(
                word["duration"].total_seconds() * 10000000
            )  # Convert to 100-nanosecond units
            end_time = word["audio_offset"] + duration_microseconds

            srt_file.write(f"{subtitle_index}\n")
            srt_file.write(
                f"{format_time(current_start)} --> {format_time(end_time)}\n"
            )
            srt_file.write(f"{''.join(current_line)}\n\n")

            subtitle_index += 1
            current_line = []
            current_start = None


def text_to_speech_with_subtitle(
    speech_key, service_region, text, audio_path, srt_path
):
    """Convert text to speech and generate subtitle"""
    try:
        # Configure speech service
        speech_config = speechsdk.SpeechConfig(
            subscription=speech_key, region=service_region
        )
        speech_config.speech_synthesis_voice_name = "ja-JP-ShioriNeural"

        # Configure audio output
        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio_path)

        # Create speech synthesizer
        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )

        # Store word boundaries for subtitle generation
        word_boundaries = []

        def handle_word_boundary(evt):
            word_boundaries.append(
                {
                    "text": evt.text,
                    "audio_offset": evt.audio_offset,
                    "duration": evt.duration,  # This is a timedelta object
                }
            )

        # Subscribe to word boundary event
        speech_synthesizer.synthesis_word_boundary.connect(handle_word_boundary)

        # Perform synthesis
        result = speech_synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text [{text}]")
            # Generate subtitle file
            create_srt(word_boundaries, srt_path)
            print(f"Audio saved to: {audio_path}")
            print(f"Subtitle saved to: {srt_path}")
            return True
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")
            return False

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback

        print(traceback.format_exc())
        return False


def main():
    # Azure credentials
    speech_key = "6SSkROmS0L0n8t9H7YE52CvYy5Va7qotlyh6QpEL4okJNYCaAcqwJQQJ99AKACi0881XJ3w3AAAYACOGqH7h"
    service_region = "japaneast"

    # Input text
    text = """
次に、非常に重要な概念について説明します：生成系AIです。皆さんはきっと、最近話題のChatGPTや、Midjourney、作曲ができるAIなどについて聞いたことがあると思います。では、生成系AIとは一体何なのでしょうか？
ここで強調したいのですが、生成系AIとは、構造化された複雑な情報を生成できるAIモデルのことです。【停顿10秒】この説明は少し抽象的に聞こえるかもしれませんので、具体的な例を見ていきましょう。
一つ考えていただきたい質問があります：作文を書く、絵を描く、曲を作る、これらのタスクには共通点があるでしょうか？【停顿15秒】
そうですね。これらのタスクはすべて、新しいコンテンツを「創造する」必要があります。生成系AIは、このような創造的なタスクを遂行できるAIなのです。生成できるものには以下があります：

テキストについては、物語を書いたり、質問に答えたり、さらには詩を書いたりすることができるものです。
画像に関しては、説明に基づいて様々な画像を描き出すことが可能です。
音声については、音楽を生成したり、人の声を模倣したりすることができます。
構造化データについては、表やグラフなどのデータを自動的に生成することができます。

日常生活での例をいくつか挙げてみましょう。【停顿5秒】
カーナビを使用していると、「200メートル先を左折してください」という音声が流れますが、これはAIが生成した音声です。また、多くの人が使用している自撮りアプリの美顔機能は、リアルタイムで加工された画像を生成しています。若い方々の中には、AI文章作成アシスタントを使って文章を書いた経験がある人もいるでしょう。これらはすべて生成系AIの応用例です。
ここで考えていただきたい興味深い点があります：なぜ生成系AIが生成するものを「構造化された複雑な情報」と呼ぶのでしょうか？【停顿10秒】
簡単な例で説明してみましょう。ケーキを作ることを想像してください。小麦粉、卵、牛乳などの材料が必要で、これらの材料を特定の割合と手順で組み合わせることで、おいしいケーキができあがります。生成系AIも同じように、様々な情報要素（テキストや画像の基本的な構成要素など）を特定のルールに従って組み合わせることで、意味のあるコンテンツを生成しているのです。
最後に、特に付け加えたい点があります。皆さんもお気づきかもしれませんが、生成系AIの出力は完全に予測することができません。例えば、AIに春についての作文を10編書かせると、それぞれ少しずつ異なる内容になります。これは、10人の人に同じテーマで作文を書かせると、それぞれ異なる作文になるのと同じです。この「不確実性」こそが、生成系AIの重要な特徴の一つなのです。

    """

    # Output paths
    audio_path = "output.wav"
    srt_path = "output.srt"

    # Generate speech and subtitle
    text_to_speech_with_subtitle(
        speech_key=speech_key,
        service_region=service_region,
        text=text,
        audio_path=audio_path,
        srt_path=srt_path,
    )


if __name__ == "__main__":
    main()
