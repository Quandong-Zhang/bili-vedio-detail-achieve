import waybackpy
import sys
from lxml import etree
import requests
import json
import logging
from time import sleep

VERSION = "0.0.1"
UA = "Bilibili vedio detail saver {VERSION}"
GLOBE_SLEEP_TIME = 0
WEB_ACHIEVE_LIMIT = 30

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info("Bilibili vedio detail saver {VERSION} started".format(VERSION=VERSION))

def save_vedio_detail(bvid):
    save_obj = waybackpy.WaybackMachineSaveAPI("https://api.bilibili.com/x/web-interface/view?bvid={bvid}".format(bvid=bvid), UA)
    return save_obj.save()

def get_last_saved_detail_obj(bvid):
    cdx_api = waybackpy.WaybackMachineCDXServerAPI("https://api.bilibili.com/x/web-interface/view?bvid={bvid}".format(bvid=bvid), UA)
    return cdx_api.newest()

def get_original_api(bvid):
    plain_api_res = requests.get(get_last_saved_detail_obj(bvid).archive_url, headers={"User-Agent": UA})
    logger.info("plain_api_res: %s", plain_api_res.text)
    return json.loads(plain_api_res.text)

def save_user_all_list(mid):
    #https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid=499106648&jsonp=jsonp
    folders = json.loads(requests.get("https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid={mid}&jsonp=jsonp".format(mid=mid), headers={"User-Agent": UA, "Referer": "https://space.bilibili.com/{mid}/favlist".format(mid=mid)}).text)["data"]["list"]
    sleep(GLOBE_SLEEP_TIME)
    logger.info("folders: %s", folders)
    for folder in folders:
        logger.info("folder: %s", folder)
        folder_id = folder["id"]
        folder_name = folder["title"]
        logger.info("folder_id: %s", folder_id)
        logger.info("folder_name: %s", folder_name)
        folder_res = json.loads(requests.get("https://api.bilibili.com/x/v3/fav/resource/list?media_id={folder_id}&pn=1&ps=20&keyword=&order=mtime&type=0&tid=0&jsonp=jsonp".format(folder_id=folder_id), headers={"User-Agent": UA, "Referer": "https://space.bilibili.com/{mid}/favlist".format(mid=mid)}).text)
        sleep(GLOBE_SLEEP_TIME)
        logger.info("folder_res: %s", folder_res)
        for vedio in folder_res["data"]["medias"]:
            logger.info("vedio: %s", vedio)
            bvid = vedio["bvid"]
            logger.info("bvid: %s", bvid)
            save_vedio_detail(bvid)
            sleep(WEB_ACHIEVE_LIMIT)

def save_region_all_list(rid):
    #https://api.bilibili.com/x/web-interface/newlist?rid=1&type=0&pn=1&ps=20&jsonp=jsonp
    region_res = json.loads(requests.get("https://api.bilibili.com/x/web-interface/newlist?rid={rid}&type=0&pn=1&ps=20&jsonp=jsonp".format(rid=rid), headers={"User-Agent": UA}).text)
    sleep(GLOBE_SLEEP_TIME)
    logger.info("region_res: %s", region_res)
    for vedio in region_res["data"]["archives"]:
        logger.info("vedio: %s", vedio)
        bvid = vedio["bvid"]
        logger.info("bvid: %s", bvid)
        save_vedio_detail(bvid)
        sleep(WEB_ACHIEVE_LIMIT)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        logger.info("No arguments, exiting...")
        sys.exit()
    elif sys.argv[1] == "user":
        save_user_all_list(sys.argv[2])
    elif sys.argv[1] == "region":
        save_region_all_list(sys.argv[2])
    else:
        logger.info("Unknown arguments, exiting...")
        sys.exit()