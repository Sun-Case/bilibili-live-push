import asyncio
import aiohttp
from aiohttp_socks import ProxyConnector

"""
数据分析

在控制台中输入 `ytInitialData` 可得到一个 Object，里面有需要的数据

ytInitialData (Object) = {
    content (Object) = {
        twoColumnBrowseResultsRenderer (Object) = {
            tabs (Array) = [
                (Object) = {
                    tabRenderer (Object) = {
                        content (Object) = {
                            sectionListRenderer (Object) = {
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
                                                                    startTime (string)
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
                                                                }
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
                                                                        simpleText (string) // 直播标题
                                                                    }
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

if __name__ == "__main__":
    pass
