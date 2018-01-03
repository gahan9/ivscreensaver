# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcaddon
import xbmcvfs
from bs4 import BeautifulSoup
from xml.etree.ElementTree import parse, Element
from videomaker import VideoMaker
import launchplugin
from md5_check import get_directory_hash


def print_log(*args):
    try:
        prefix = ADDON_ID
    except NameError:
        prefix = "CUSTOM_NOTICE>> "
    arg = "\n".join([str(a) for a in args])
    try:
        xbmc.log("{0} :: {1}".format(prefix, arg), 2)
    except NameError:
        import xbmc
        xbmc.log("{0} :: {1}".format(prefix, arg), 2)
    except ImportError:
        print("{0} :: {1}".format(prefix, arg))


# CONSTANTS
ADDON_ID = 'screensaver.customslideshow'
ADDON = xbmcaddon.Addon(id=ADDON_ID)
CWD = ADDON.getAddonInfo('path').decode("utf-8")
XBMC_HOME = xbmc.translatePath('special://home/')
XBMC_USER_DATA = xbmc.translatePath('special://home/userdata')
ADDON_HOME = os.path.join(XBMC_HOME, 'addons', ADDON_ID)
CACHE_DATA_FOLDER = os.path.join(XBMC_USER_DATA, 'addon_data', ADDON_ID)
LABELS = {0: 'EVEN_PICTURES', 1: 'ODD_PICTURES'}
ADDON_RESOURCE_SETTING = os.path.join(ADDON_HOME, 'resources', 'settings.xml')
CACHE_SETTING_FILE = os.path.join(CACHE_DATA_FOLDER, 'settings.xml')

print_log("      SCREEN_SAVER_ADDON_INITIALIZED...      ",
          "ADDON_ID   : {0}".format(ADDON_ID),
          "ADDON      : {0}".format(ADDON),
          "CWD        : {0}".format(CWD),
          "XBMC_HOME  : {0}".format(XBMC_HOME),
          "XBMC_USER_DATA  : {0}".format(XBMC_USER_DATA),
          "ADDON_HOME : {0}".format(ADDON_HOME),
          "ADDON_RESOURCE_SETTING : {0}".format(ADDON_RESOURCE_SETTING),
          "CACHE_SETTING_FILE : {0}".format(CACHE_SETTING_FILE)
          )

if not os.path.exists(CACHE_DATA_FOLDER):
    xbmcvfs.mkdir(CACHE_DATA_FOLDER)

if not os.path.exists(CACHE_SETTING_FILE):
    with open(CACHE_SETTING_FILE, "a+") as cache_media:
        xml_default_content = """<settings>
                        <setting id="dimLevel" value="0" />
                        <setting id="initiate_me" value="10" />
                        <setting id="odd_even_is_enabled" value="true" />
                        <setting id="select_media_even" value="" />
                        <setting id="select_media_odd" value="" />
                        <setting id="time" value="3" />
                        <setting id="useFolder" value="true" />
                    </settings>
                    """
        cache_media.write(xml_default_content)
        print_log("create file xml")
_image_extension = [".png", ".jpeg", ".jpg"]
_video_extension = [".mp4", ".mkv", ".avi"]


def insert_data(content_list=None, content_location=None, flag=0, target_xml=ADDON_RESOURCE_SETTING):
    print_log("insert_data() : initialized")
    xml_doc = parse(target_xml)
    xml_root = xml_doc.getroot()
    label = LABELS[flag]
    category = xml_root.findall('.//category[@label="' + label + '"]')[0]
    # print_log("content_list", content_list, "content_location", content_location, "flag", flag, "target_xml", target_xml)
    if content_list:
        for content in content_list:
            if content.split('.')[-1] in ['mp4', 'mkv']:
                label = '.'.join(content.split(".")[:-1])
                category.append(
                    Element("setting",
                            {"label": label,
                             "type": "slider", "default": "5",
                             "range": "0,30",
                             "option": "int",
                             "id": content
                             }))
    if content_location:
        if os.path.exists(content_location):
            for content in os.listdir(content_location):
                if content.endswith(".mp4") or content.endswith(".mkv"):
                    label = '.'.join(content.split(".")[:-1])
                    category.append(
                        Element("setting",
                                {"label": label,
                                 "type": "slider", "default": "5",
                                 "range": "0,30",
                                 "option": "int",
                                 "id": content
                                 }))
    xml_doc.write(target_xml, xml_declaration=True)
    print_log("insert_data() : xml updated")


def remove_xml(target_xml=ADDON_RESOURCE_SETTING, label=LABELS[0]):
    print_log("remove_xml() : initialized")
    xml_doc = parse(target_xml)
    xml_root = xml_doc.getroot()
    for category in xml_root:
        if 'label' in category.attrib:
            if category.attrib['label'] == label:
                for elem in list(category):
                    category.remove(elem)
    xml_doc.write(target_xml, xml_declaration=True)
    print_log("remove_xml() : xml tag successfully cleared")


def writexml(path, flag=0):
    print_log("writexml() : initialized")
    if os.path.exists(path):
        print_log(path)
        remove_xml(label=LABELS[flag])
        cache_folder = os.path.join(path, ".cache")
        if not os.path.exists(cache_folder):
            os.mkdir(cache_folder)
        xbmc.executebuiltin("ActivateWindow(busydialog)")
        xbmc.sleep(100)
        converter_obj = VideoMaker()
        source = os.listdir(path)
        print_log("source image list", source, converter_obj.supported_extension)
        for content in source:
            content_extension = content.split(".")[-1]
            if content_extension in ['jpg', 'jpeg', 'png']:
                converter_obj.make_video_ffmpeg(content, source_path=path, target_path=cache_folder, duration=8)
                print("Process for {} completed".format(content))
        # print_log(os.listdir(cache_folder), path)
        target_list = os.listdir(cache_folder)
        target_content = ['.'.join(content.split(".")[:-1]) for content in target_list]
        source_content = ['.'.join(content.split(".")[:-1]) for content in source]
        for file in target_content:
            if file not in source_content:
                for elem in target_list:
                    if elem.startswith(file):
                        os.remove(os.path.join(cache_folder, elem))
        insert_data(content_list=os.listdir(cache_folder), flag=flag)
        insert_data(content_list=os.listdir(path), flag=flag)
        xbmc.sleep(100)
        xbmc.executebuiltin("Dialog.Close(busydialog)")
        with open(os.path.join(ADDON_HOME, "{}.md5".format(LABELS[flag])), "w") as f:
            f.write(get_directory_hash(path))
        print_log("writexml() : progress 100%")


def readxml(directory_items, target_xml=ADDON_RESOURCE_SETTING):
    print_log("readxml() : initialized")
    with open(target_xml, "r") as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')
        settings = soup.find_all("category")
        for sett in settings:
            setting_tags = sett.find_all("setting")
            if LABELS[0] in sett["label"]:  # EVEN_PICTURES
                even_images_from_settings = setting_tags if setting_tags else None
                if even_images_from_settings:
                    new_images_in_even_folder_exists = os.listdir(directory_items.get("select_media_even"))
                    if len(even_images_from_settings) != len(new_images_in_even_folder_exists):
                        writexml(directory_items.get("select_media_even"), flag=0)
            if LABELS[1] in sett["label"]:  # ODD_PICTURES
                odd_images_from_settings = setting_tags if setting_tags else None
                if odd_images_from_settings:
                    new_images_in_odd_folder_exists = os.listdir(directory_items.get("select_media_odd"))
                    if len(odd_images_from_settings) != len(new_images_in_odd_folder_exists):
                        writexml(directory_items.get("select_media_odd"), flag=1)


def check_new_path(target_xml=CACHE_SETTING_FILE):
    if os.path.exists(target_xml):
        with open(target_xml, "r") as f:  # opening xml file
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            settings = soup.find_all("setting")
            # for old python version use below line
            media_dict = dict((sett["id"], sett["value"]) for sett in settings if "select_media" in sett["id"])
            # media_dict = {sett["id"]: sett["value"] for sett in settings if "select_media" in sett["id"]}
            return media_dict
    else:
        return "File not found"


class BaseMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        return True


if __name__ == '__main__':
    print_log("VideoScreenSaverService: Startup checks")
    # Make sure that the settings have been updated correctly
    media_data_path = check_new_path()
    monitor = BaseMonitor()
    # Check if we should start the screen saver video on startup
    launchplugin.main()
    while not monitor.abortRequested():
        xbmc.sleep(500)
        if monitor.abortRequested():
            xbmc.sleep(500)
            os._exit(1)

        recursive_path_check = check_new_path()
        print_log("path_recursion", recursive_path_check)

        if monitor.onSettingsChanged():
            # print_log("Settings Changed")
            if 'select_media_odd' in media_data_path and 'select_media_odd' in recursive_path_check:
                if not media_data_path['select_media_odd'] == recursive_path_check['select_media_odd']:
                    print_log("odd_change_trigger")
                    get_odd_path = recursive_path_check.get("select_media_odd")
                    writexml(get_odd_path, flag=1)

            if 'select_media_even' in media_data_path and 'select_media_even' in recursive_path_check:
                if not media_data_path['select_media_even'] == recursive_path_check['select_media_even']:
                    print_log("even_change_trigger")
                    get_even_path = recursive_path_check.get("select_media_even")
                    writexml(get_even_path, flag=0)
            media_data_path = check_new_path()
        else:
            xbmc.sleep(500)
            if 'select_media_odd' in recursive_path_check:
                get_odd_path = recursive_path_check.get("select_media_odd")
                odd_md5 = os.path.join(ADDON_HOME, "{}.md5".format(LABELS[1]))
                if os.path.exists(odd_md5):
                    with open(odd_md5, "r") as f:
                        existing_md5 = f.read().strip()
                        new_md5 = get_directory_hash(get_odd_path)
                        if new_md5 != existing_md5:
                            print_log("odd_md5_trigger", existing_md5, new_md5)
                            writexml(get_odd_path, flag=1)
                else:
                    with open(odd_md5, 'w') as f:
                        f.write(get_directory_hash(get_odd_path))
            if 'select_media_even' in recursive_path_check:
                get_even_path = recursive_path_check.get("select_media_even")
                even_md5 = os.path.join(ADDON_HOME, "{}.md5".format(LABELS[0]))
                if os.path.exists(even_md5):
                    with open(even_md5, "r") as f:
                        existing_md5 = f.read().strip()
                        if get_directory_hash(get_even_path) != existing_md5:
                            print_log("even_md5_trigger", existing_md5, even_md5)
                            writexml(get_even_path, flag=0)
                else:
                    with open(even_md5, 'w') as f:
                        f.write(get_directory_hash(get_even_path))

