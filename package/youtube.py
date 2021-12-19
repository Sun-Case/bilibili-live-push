import asyncio
from typing import Optional, Dict, Any

import aiohttp
from aiohttp_socks import ProxyConnector
from typing import *
import re
import json

"""
数据分析

在控制台中输入 `ytInitialData` 可得到一个 Object，里面有需要的数据

ytInitialData (Object) = {
    contents (Object) = {
        twoColumnBrowseResultsRenderer (Object) = {
            tabs (Array) = [
                (Object) = {
                    tabRenderer (Object) = {
                        content (Object) = {
                            sectionListRenderer (Object) = {
                                contents (Array) = [
                                    (Object) = {
                                        itemSectionRenderer (Object) = {
                                            contents (Array) = [
                                                (Object) = {
                                                    shelfRenderer (Object) = {
                                                        content (Object) = {
                                                            expandedShelfContentsRenderer (Object) = {
                                                                items (Array) = [
                                                                    // 下面的 Object 为 即将直播的 Object
                                                                    (Object) = {
                                                                        videoRenderer (Object) = {
                                                                            upcomingEventData (Object) = {  // 即将直播才会有该字段
                                                                                isReminderSet (bool)
                                                                                startTime (string)  // 字符串类型的时间戳，单位：秒
                                                                                upcomingEventText (Object) = {
                                                                                    runs (Array) = [
                                                                                        (Object) = {
                                                                                            text (string) = "预定发布时间"
                                                                                        }
                                                                                        (Object) = {
                                                                                            text (string) = "DATE_PLACEHOLDER"
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            }
                                                                            title (Object) = {
                                                                                simpleText (string) // 直播标题
                                                                                accessibility (Object) = {
                                                                                    accessibilityData (Object) = {
                                                                                        label (string) // 直播间详细标题
                                                                                    }
                                                                                }
                                                                            }
                                                                            thumbnailOverlays (Array) = [
                                                                                (Object) = {
                                                                                    thumbnailOverlayTimeStatusRenderer (Object) = {
                                                                                        style (string) = "UPCOMING"
                                                                                        text (Object) = {
                                                                                            accessibility (Object) = {
                                                                                                accessibilityData (Object) = {
                                                                                                    label (string) = "直播"
                                                                                                }
                                                                                            }
                                                                                        }
                                                                                    }
                                                                                }
                                                                            ]
                                                                            videoId (string) // 直播间ID
                                                                        }
                                                                    }
                                                        
                                                                    // 下面的 Object 为 正在直播的 Object
                                                                    (Object) = {
                                                                        videoRenderer (Object) = {
                                                                            descriptionSnippet (Object) = {
                                                                                runs (Array) = [
                                                                                    text (string) // 直播简介
                                                                                ]
                                                                            }
                                                                            thumbnailOverlays (Array) = [
                                                                                (Object) = {
                                                                                    thumbnailOverlayResumePlaybackRenderer (Object) = {
                                                                                        percentDurationWatched (int) // 观看进度，如果正在直播时打开过直播间，则为 100
                                                                                    }
                                                                                }
                                                                                (Object) = {
                                                                                    thumbnailOverlayTimeStatusRenderer (Object) = {
                                                                                        icon (Object) = {
                                                                                            iconType (string) = "LIVE" // 正在直播
                                                                                        }
                                                                                        style (string) = "LIVE"
                                                                                    }
                                                                                }
                                                                                (Object) = {
                                                                                    thumbnailOverlayNowPlayingRenderer (Object) = {
                                                                                        text (Object) = {
                                                                                            runs (Array) = [
                                                                                                (Object) = {
                                                                                                    text (string) = "正在播放"
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    }
                                                                                }
                                                                            ]
                                                                            title (Object) = {
                                                                                accessibility (Object) = {
                                                                                    accessibilityData (Object) = {
                                                                                        label (string) // 直播详细标题
                                                                                    }
                                                                                }
                                                                                simpleText (string) // 直播标题, channelFeaturedContentRenderer 没有该字段
                                                                                runs (Array) = [
                                                                                    (Object) = {
                                                                                        text (string) // 与 simpleText 作用相同
                                                                                    }
                                                                                ]
                                                                            }
                                                                            viewCountText (Object) = {
                                                                                runs (Array) = [
                                                                                    (Object) = {
                                                                                        text (string) // 人数
                                                                                    }
                                                                                    (Object) = {
                                                                                        text (string) = "人正在观看"
                                                                                    }
                                                                                ]
                                                                            }
                                                                            showViewCountText (Object) // 同 viewCountText
                                                                            videoId (string) // 直播间ID
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        }
                                                    }
                                                    channelFeaturedContentRenderer (Object) = { // channelFeaturedContentRenderer 意味着主页的第一个位置放置的是正在直播（因为有的 Youtuber 主页的第一个位置放的是一个视频）
                                                        items (Array) // 和 shelfRenderer.content.expandedShelfContentsRenderer.item 结构一致
                                                    }
                                                }
                                            ]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        }
    }
}
"""


class YTB:
    page_source: str = ""
    ytInitialData: Dict = {}
    items: List[Dict] = []

    def __init__(self, channel: str, proxy: str):
        assert channel, "channel 为空"
        self.channel = f"https://www.youtube.com/channel/{channel}"
        self.connector = None if not proxy else ProxyConnector.from_url(proxy)

    def __get_ready_live__(self) -> List:
        live_data = []

        for item in self.items:  # type: dict
            if "upcomingEventData" not in item.get("videoRenderer", {}):
                continue

            video_renderer: dict = item["videoRenderer"]
            live_data.append({
                "videoId": video_renderer["videoId"],
                "simpleTitle": video_renderer["title"]["simpleText"],
                "longTitle": video_renderer["title"]["accessibility"]["accessibilityData"]["label"],
                "description": video_renderer["descriptionSnippet"]["runs"][0]["text"],
                "startTime": int(video_renderer["upcomingEventData"]["startTime"])
            })

        return live_data

    def __get_living__(self) -> Optional[dict[Any, Any]]:
        live_data = {}

        for item in self.items:  # type: dict
            state = False
            for thumbnail in item.get("videoRenderer", {}).get("thumbnailOverlays", []):  # type: dict
                if thumbnail.get("thumbnailOverlayTimeStatusRenderer", {}).get("style", "") == "LIVE":
                    state = True
                    break

            if state is False:
                continue

            video_renderer: dict = item["videoRenderer"]
            live_data["videoId"] = video_renderer["videoId"]
            live_data["count"] = video_renderer["viewCountText"]["runs"][0]["text"]
            live_data["simpleTitle"] = video_renderer["title"]["simpleText"] if "simpleText" in video_renderer[
                "title"] else video_renderer["title"]["runs"][0]["text"]
            live_data["longTitle"] = video_renderer["title"]["accessibility"]["accessibilityData"]["label"]
            live_data["description"] = video_renderer["descriptionSnippet"]["runs"][0]["text"]

            return live_data

        return None

    def __get_items__(self) -> bool:
        tabs: List[Dict] = []
        for tab in self.ytInitialData.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", []):
            tabs.append(tab)

        contents: List[Dict] = []
        for tab in tabs:  # type: dict
            contents += tab.get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", [])

        _contents_: List[Dict] = []
        for content in contents:  # type: dict
            _contents_ += content.get("itemSectionRenderer", {}).get("contents", [])

        for content in _contents_:
            self.items += content.get("shelfRenderer", {}).get("content", {}).get("expandedShelfContentsRenderer",
                                                                                  {}).get("items", [])
        for content in _contents_:
            self.items += content.get("channelFeaturedContentRenderer", {}).get("items", [])

        return True

    def __get_ytInitialData__(self) -> bool:
        pattern = re.compile(r"var ytInitialData = (.*?);</script>")
        find = pattern.findall(self.page_source)
        if len(find) == 1:
            try:
                self.ytInitialData = json.loads(find[0])
            except Exception as e:
                print(e)
                return False
        else:
            return False
        return True

    async def __get_page_source__(self) -> bool:
        try:
            async with aiohttp.ClientSession(connector=self.connector) as session:
                resp = await session.get(self.channel)
                self.page_source = await resp.text()
        except Exception as e:
            print(e)
            return False
        return True


if __name__ == "__main__":
    ytb = YTB("", "")
    loop = asyncio.get_event_loop()
    tasks = [
        asyncio.ensure_future(ytb.__get_page_source__())
    ]
    loop.run_until_complete(asyncio.wait(tasks))
    ytb.__get_ytInitialData__()
    ytb.__get_items__()
    print(ytb.__get_living__())
    print(ytb.__get_ready_live__())
