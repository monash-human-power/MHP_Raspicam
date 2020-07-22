import cv2
import numpy as np

from backend import Backend, PublishFunc
from canvas import Canvas

class OpenCVStaticImageBackend(Backend):
    """ Displays a static, local image in place of a video feed.
        Uses the OpenCV (`cv2`) library. """

    def __init__(self, width: int, height: int, publish_recording_status_func: PublishFunc, publish_errors_func: PublishFunc):
        super().__init__(width, height, publish_recording_status_func, publish_errors_func)

        self.background = np.zeros((self.height, self.width, 4), np.uint8)

        framerate = 60
        # Time between video frames when running on OpenCV, in milliseconds
        self.frametime = int(1000 / framerate)

        self.base_canvas = Canvas(self.width, self.height)
        self.data_canvas = Canvas(self.width, self.height)
        self.message_canvas = Canvas(self.width, self.height)

    def start_video(self) -> None:
        # Nothing to do
        pass

    def set_background(self, image_path: str) -> None:
        background_original = cv2.imread(cv2.samples.findFile(image_path))
        self.background = cv2.resize(background_original, (self.width, self.height))

    def on_base_canvas_updated(self, base_canvas: Canvas) -> None:
        try:
            self.base_canvas = base_canvas
        except:
            self.send_camera_error()

    def on_canvases_updated(self, data_canvas: Canvas, message_canvas: Canvas) -> None:
        try:
            self.data_canvas = data_canvas
        except:
            self.send_camera_error() # data overlay error
        
        try:
            self.message_canvas = message_canvas
        except:
            self.send_camera_error() # message overlay error

    def _on_loop(self) -> None:
        """ This function uses the cached overlays, as OpenCV needs us to
            manually add it to each frame. """
        frame = self.background

        frame = self.base_canvas.copy_to(frame)
        frame = self.data_canvas.copy_to(frame)
        frame = self.message_canvas.copy_to(frame)

        cv2.imshow('frame', frame)
        cv2.waitKey(self.frametime)

    def stop_video(self) -> None:
        cv2.destroyAllWindows()
