#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import os
import threading
from shutil import copyfile

try:
    import xbmc
except ImportError:
    pass

try:
    ADDON_ID = 'screensaver.video-12'
    ADDON_PATH = xbmc.translatePath('special://home/addons/'+ADDON_ID)
    if not os.path.exists(ADDON_PATH):
        try:
            from service import ADDON_HOME
            from service import ADDON_ID
            ADDON_PATH = xbmc.translatePath('special://home/addons/' + ADDON_ID)
        except Exception as e:
            pass
except NameError:
    ADDON_PATH = os.getcwd()


def print_log(*args):
    try:
        if 'ADDON_ID' not in globals() and 'ADDON_ID' not in locals():
            ADDON_ID = "CUSTOM_NOTICE>> "
        prefix = ADDON_ID
    except:
        prefix = "CUSTOM_NOTICE>> "
    for arg in args:
        try:
            import xbmc
            xbmc.log("{} :: {}".format(prefix, arg), 2)
        except ImportError:
            print("{} :: {}".format(prefix, arg))


def set_env(**kwargs):
    for key, value in kwargs.items():
        os.environ[key] = value


class FileNotFoundError(Exception):
    """Raised when the file does not exists"""

    def __init__(self, *args, **kwargs):
        print_log("File not exists : {0}".format(args))
        Exception.__init__(self, *args, **kwargs)


class VideoMaker(object):
    def __init__(self, *args, **kwargs):
        set_env(ffmpeg=ADDON_PATH)
        print_log("{:^25}".format("__INITIALIZED__"))
        self.supported_extension = ['jpg', 'jpeg', 'png']
        self.video_extension = ['mp4', 'mkv']
        self.codec = kwargs['codec'] if 'codec' in kwargs else "mp4v"
        self.fps = kwargs['fps'] if 'fps' in kwargs else 2
        self.duration = 5
        self.width = '1920'
        self.height = '1080'

    def execute(self, path=None, duration=5, target_path=None, multi_threading=False, **kwargs):
        contents = os.listdir(path)
        target_path = target_path if target_path else os.path.join(path, ".cache")
        if not os.path.exists(target_path):
            try:
                os.mkdir(target_path)
            except Exception as e:
                print_log(e)
                os.makedirs(target_path)
        if contents:
            if multi_threading:
                threading.Thread(target=self.convert_bulk, args=(contents, path, target_path, duration )).start()
            else:
                self.convert_bulk(contents, path, target_path, duration)
            return {"status": "Processing completed", "target_path": target_path}

    def convert_bulk(self, contents, path, target_path, duration):
        for content in contents:
            content_extension = content.split(".")[-1]
            if content_extension in self.supported_extension:
                self.make_video_ffmpeg(content, source_path=path, target_path=target_path, duration=duration)
                print("Process for {} completed".format(content))
            elif content_extension in self.video_extension:
                # by change if content is video
                pass
        # return {"status": "Processing completed", "target_path": self.target_path}

    def make_video_ffmpeg(self, content, source_path=None, target_path=None, flag="keep", **kwargs):
        """
        BASE_COMMAND C:\Users\Quixom\AppData\Roaming\Kodi\addons\screensaver.video-12\ffmpeg.exe -loop 1 -i C:\Users\Quixom\AppData\Roaming\Kodi\ScreenSaver_ADDON\even_anonymous\anonymous_1920x1200.jpg -c:v libx264 -t 5 -pix_fmt yuv420p -vf scale=1920:1080 C:\Users\Quixom\AppData\Roaming\Kodi\ScreenSaver_ADDON\even_anonymous\.cache\a.mp4
        BASE_COMMAND <ffmpeg-exe> -loop 1 -i <image_path> -c:v libx264 -t 5 -pix_fmt yuv420p -vf scale=1920:1080 <target-video>
        :param content: full absolute image path
        :param source_path: image location
        :param target_path: store video at this location
        :param kwargs:
        :param flag: flag set to decide whether video need to generate for image or not
            flag='remove': to remove/overwrite file
        :return:
        """
        try:
            from ffmpy import ffmpy  # placed module in local
        except ImportError:
            raise FileNotFoundError("Dependency of ffmpeg broke!!!")
        duration = kwargs['duration'] if 'duration' in kwargs else self.duration
        input_image = os.path.join(source_path, content)  # set path for input location
        output_video_name = content.split('.')[-2] + ".mp4"  # name the output video
        output_video = os.path.join(target_path, output_video_name)  # set path for output location
        # setup scale for video set to default values if no argument passed
        scale = "{}:{}".format(kwargs['w'], kwargs['h']) if 'w' in kwargs and 'h' in kwargs \
            else "{}:{}".format(self.width, self.height)
        # set output setting flags like duration encoding etc.
        output_settings = "-c:v libx264 -t {} -pix_fmt yuv420p -vf scale={}".format(duration, scale)
        ff = ffmpy.FFmpeg(
            inputs={input_image: '-loop 1'},  # loop to iterate same image again and again
            outputs={output_video: output_settings}
        )
        """
        ff = ffmpy.FFmpeg(
            inputs={r"C:\Users\Quixom\AppData\Roaming\Kodi\ScreenSaver_ADDON\even_anonymous\0124654c7950f4f823c1092c60837ccc.jpg": '-loop 1'},
            outputs={r"C:\Users\Quixom\AppData\Roaming\Kodi\ScreenSaver_ADDON\even_anonymous\.cache\0124654c7950f4f823c1092c60837ccc.mp4": "-c:v libx264 -t 5 -pix_fmt yuv420p -vf scale=1920:1080"}
        )
        """
        # print_log(input_image, output_video, output_settings, ff.cmd)
        if os.path.exists(output_video):
            if flag == "remove":
                try:
                    os.remove(output_video)  # remove existing video to avoid any overwrite exception
                    os.popen(ff.cmd)
                except WindowsError:
                    pass
        else:
            os.popen(ff.cmd)


def main(image_list):
    set_env(ffmpeg=ADDON_PATH)
    obj = VideoMaker()
    try:
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        obj.execute(path=image_list)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
    except NameError:
        obj.execute(path=image_list)
