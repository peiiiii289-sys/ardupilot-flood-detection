import argparse
import time

import cv2

from camera.video_source import VideoSource


class CameraStream:
    """
    C 組正式影像輸入模組。

    支援：
    1. Webcam
    2. Android HTTP / MJPEG / RTSP
    3. 本機 MP4
    4. 手機斷線後切換 MP4
    5. fallback MP4 自動循環
    """

    def __init__(
        self,
        source: int | str = 0,
        fallback_source: str | None = None,
    ):
        self.primary_source = source
        self.fallback_source = fallback_source

        self.current_source = source
        self.using_fallback = False

        self.video = VideoSource(
            source=source,
            loop=False,
        )

        self.buffered_frame = None

        if not self.video.is_opened():
            if not self._switch_to_fallback():
                raise RuntimeError(
                    f"無法開啟主要影像來源："
                    f"{source}"
                )

    def _switch_to_fallback(
        self,
    ) -> bool:

        if self.fallback_source is None:
            return False

        if self.using_fallback:
            return False

        print(
            "主要影像來源失敗，"
            "準備切換備援影片："
            f"{self.fallback_source}"
        )

        # 先完整釋放手機 MJPEG / RTSP
        self.video.release()

        # Windows / FFmpeg 有時需要短暫時間
        # 釋放上一個 decoder
        time.sleep(0.5)

        # 最多嘗試三次開啟備援影片
        for attempt in range(1, 4):

            fallback = VideoSource(
                source=self.fallback_source,
                loop=True,
            )

            if fallback.is_opened():

                # 不只檢查 isOpened，
                # 必須實際讀到第一個 Frame。
                ok, frame = (
                    fallback.get_frame()
                )

                if ok and frame is not None:

                    self.video = fallback
                    self.current_source = (
                        self.fallback_source
                    )
                    self.using_fallback = True

                    # 第一張已經讀到了，
                    # 暫存起來，不要丟掉。
                    self.buffered_frame = frame

                    print(
                        "備援影片切換成功："
                        f"{self.fallback_source}"
                    )

                    return True

            fallback.release()

            print(
                f"備援影片第 {attempt} 次"
                "開啟失敗，重新嘗試..."
            )

            time.sleep(0.5)

        print(
            "備援影片無法取得 Frame："
            f"{self.fallback_source}"
        )

        return False

    def is_opened(self) -> bool:
        return self.video.is_opened()

    def get_frame(self):

        # 切換 fallback 時已經預讀第一張
        if self.buffered_frame is not None:
            frame = self.buffered_frame
            self.buffered_frame = None
            return True, frame

        ok, frame = self.video.get_frame()

        if ok:
            return True, frame

        # 主要來源失敗
        if not self.using_fallback:

            if self._switch_to_fallback():

                if self.buffered_frame is not None:
                    frame = self.buffered_frame
                    self.buffered_frame = None
                    return True, frame

        return False, None

    def release(self) -> None:
        self.video.release()


def preview_camera(
    source: int | str = 0,
    fallback_source: str | None = None,
) -> None:

    camera = None

    try:
        camera = CameraStream(
            source=source,
            fallback_source=fallback_source,
        )

        print(
            f"目前影像來源："
            f"{camera.current_source}"
        )

        print(
            "按 q 結束影像預覽"
        )

        while True:

            ok, frame = camera.get_frame()

            if not ok:
                print(
                    "無法繼續取得影像 Frame"
                )
                break

            cv2.imshow(
                "UAV Flood Camera",
                frame,
            )

            if (
                cv2.waitKey(1) & 0xFF
                == ord("q")
            ):
                break

    finally:

        if camera is not None:
            camera.release()

        cv2.destroyAllWindows()


def parse_source(
    value: str,
):
    if value.isdigit():
        return int(value)

    return value


def main():

    parser = argparse.ArgumentParser(
        description=(
            "UAV Flood Camera Input"
        )
    )

    parser.add_argument(
        "--source",
        default="0",
        help=(
            "主要來源：0、影片、"
            "HTTP/MJPEG 或 RTSP URL"
        ),
    )

    parser.add_argument(
        "--fallback",
        default=None,
        help=(
            "主要來源失敗後使用的 "
            "MP4 備援影片"
        ),
    )

    args = parser.parse_args()

    source = parse_source(
        args.source
    )

    preview_camera(
        source=source,
        fallback_source=args.fallback,
    )


if __name__ == "__main__":
    main()