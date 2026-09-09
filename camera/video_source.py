import cv2


class VideoSource:
    """
    統一管理 Webcam、手機串流與本機影片。
    """

    def __init__(
        self,
        source: int | str = 0,
        loop: bool = False,
    ):
        self.source = source
        self.loop = loop
        self.cap = None
        self.open()

    def open(self) -> bool:
        self.release()

        self.cap = cv2.VideoCapture(
            self.source
        )

        return self.is_opened()

    def is_opened(self) -> bool:
        return (
            self.cap is not None
            and self.cap.isOpened()
        )

    def get_frame(self):
        if not self.is_opened():
            return False, None

        ok, frame = self.cap.read()

        if ok and frame is not None:
            return True, frame

        # 備援 MP4 播完後自動從頭播放
        if self.loop:
            self.cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                0,
            )

            ok, frame = self.cap.read()

            if ok and frame is not None:
                return True, frame

            # 某些影片格式不支援直接 seek，
            # 就重新開啟影片。
            if self.open():
                ok, frame = self.cap.read()

                if ok and frame is not None:
                    return True, frame

        return False, None

    def release(self) -> None:
        if self.cap is not None:
            self.cap.release()
            self.cap = None