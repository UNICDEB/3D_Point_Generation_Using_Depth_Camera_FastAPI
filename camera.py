import pyrealsense2 as rs
import numpy as np
import cv2
import threading

class RealSenseCamera:
    def __init__(self):
        self.pipeline = rs.pipeline()
        self.config = rs.config()
        self.config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)
        self.config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
        self.profile = None
        self.intrinsics = None
        self.running = False
        self.lock = threading.Lock()

    def start(self):
        self.pipeline.start(self.config)
        self.profile = self.pipeline.get_active_profile()
        self.intrinsics = self.profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
        self.running = True

    def get_frame(self):
        if not self.running:
            return None, None, None
        frames = self.pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()

        if not depth_frame or not color_frame:
            return None, None, None

        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())

        return color_image, depth_image, depth_frame

    def pixel_to_point(self, x, y, depth_frame):
        depth = depth_frame.get_distance(x, y)
        point = rs.rs2_deproject_pixel_to_point(self.intrinsics, [x, y], depth)
        return point

    def stop(self):
        self.pipeline.stop()
        self.running = False