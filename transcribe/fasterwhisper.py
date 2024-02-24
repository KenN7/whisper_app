from fastapi import HTTPException
from faster_whisper import WhisperModel
import logging


def transcribe_file_fast(path: str = None, model_size="small"):
    try:
        # model_size = "large-v3"
        if path is None:
            raise HTTPException(status_code=400, detail="No path provided")

        # Run on GPU with FP16
        # model = WhisperModel(model_size, device="cuda", compute_type="float16")
        # or run on GPU with INT8
        # model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
        # or run on CPU with INT8
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        segments, info = model.transcribe(path, beam_size=5)

        # print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

        # for segment in segments:
        # print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
        segments = list(segments)

        return "".join(s.text for s in segments)

    except Exception as exc:
        logging.error(exc)
        raise HTTPException(status_code=400, detail=exc.__str__())
