import sonar

def _sound_section(audio):
    # VADに関する設定
    window_ms = 40
    hop_ms = 20
    lowcut = 250
    highcut = 5000
    th = None

    # VAD平滑化後処理に関する設定
    pause_ms = 500
    minlen_ms = 200

    # パワーベースのVADを実行する。window_ms, hop_msは窓幅とシフト幅。基本的に調整不要。
    # 閾値は自動的に決定されるが、自分で決めたいときは0.0~1.0の間で入力する。
    print('Run power based VAD.')
    est_label = sonar.vad.power(audio.mixdown(), window_ms=window_ms, hop_ms=hop_ms,
                                use_pre_emphasis=False, use_bandpass=False, lowcut=lowcut, highcut=highcut, th=th)

    # 推定した発話区間の平滑化を行う。
    # 検出した発話区間同士の間がpause_msの値以下の場合は発話区間を結合する。単位はms。
    # 発話区間の長さがminlen_msに達しない場合は削除する。単位はms。
    est_label = sonar.vad.post_filter(est_label, pause_ms=pause_ms, minlen_ms=minlen_ms)

    est_label = est_label.astype('ms')
    audio_ms = audio.nframes * 1000 // audio.framerate
    ss_ms = 0
    for label in est_label:
        ss_ms += label['end'] - label['start']

    rate = ss_ms / audio_ms
    return rate, ss_ms