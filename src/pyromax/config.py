# MIN_PREFERRED_BUILD = 6712

APP_VERSIONS: tuple[tuple[str, int], ...] = (
    # ("26.25.0", 6790),
    # ("26.24.0", 6784),
    # ("26.23.2", 6779),
    # ("26.23.1", 6778),
    # ("26.23.0", 6777),
    # ("26.22.2", 6773),
    # ("26.22.1", 6772),
    # ("26.22.0", 6770),
    # ("26.21.1", 6763),
    # ("26.20.2", 6758),
    # ("26.20.1", 6740),
    # ("26.19.3", 6734),
    # ("26.19.2", 6732),
    # ("26.19.1", 6729),
    # ("26.19.0", 6727),
    # ("26.18.4", 6724),
    # ("26.18.2", 6720),
    # ("26.18.1", 6716),
    # ("26.18.0", 6715),
    # ("26.17.1", 6712),
    # ("26.16.4", 6704),
    # ("26.16.3", 6702),
    # ("26.16.2", 6701),
    # ("26.16.1", 6700),
    # ("26.16.0", 6698),
    ("26.15.3", 6695),
    ("26.15.1", 6690),
    ("26.15.0", 6689),
    ("26.14.1", 6686),
    ("26.14.0", 6685),
    ("26.13.0", 6683),
    ("26.12.2", 6681),
    ("26.12.1", 6679),
    ("26.12.0", 6676),
    ("26.11.3", 6670),
    ("26.11.2", 6669),
    ("26.11.1", 6665),
    ("26.10.1", 6653),
    ("26.10.0", 6648),
    ("26.9.1", 6643),
)
ANDROID_DEVICES: tuple[tuple[str, str, str, str], ...] = (
    ("Samsung SM-A525F", "Android 13", "405dpi 405dpi 1080x2400", "arm64-v8a"),
    ("Samsung SM-A536B", "Android 14", "405dpi 405dpi 1080x2400", "arm64-v8a"),
    ("Samsung SM-A546E", "Android 14", "405dpi 405dpi 1080x2340", "arm64-v8a"),
    ("Samsung SM-G991B", "Android 14", "421dpi 421dpi 1080x2400", "arm64-v8a"),
    ("Samsung SM-G998B", "Android 13", "515dpi 515dpi 1440x3200", "arm64-v8a"),
    ("Samsung SM-S901B", "Android 14", "425dpi 425dpi 1080x2340", "arm64-v8a"),
    ("Samsung SM-S911B", "Android 14", "425dpi 425dpi 1080x2340", "arm64-v8a"),
    ("Xiaomi 2109119DG", "Android 13", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("Xiaomi 2201117TG", "Android 13", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("Xiaomi 2201123G", "Android 14", "526dpi 526dpi 1440x3200", "arm64-v8a"),
    ("Xiaomi 2210132G", "Android 14", "446dpi 446dpi 1220x2712", "arm64-v8a"),
    (
        "Xiaomi 23049PCD8G",
        "Android 14",
        "446dpi 446dpi 1220x2712",
        "arm64-v8a",
    ),
    ("Redmi 2201116TG", "Android 13", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("Redmi 22101316G", "Android 13", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("Redmi 23021RAA2Y", "Android 14", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("POCO 22011211G", "Android 13", "395dpi 395dpi 1080x2400", "arm64-v8a"),
    ("POCO 23049PCD8G", "Android 14", "446dpi 446dpi 1220x2712", "arm64-v8a"),
    ("Pixel 6", "Android 14", "411dpi 411dpi 1080x2400", "arm64-v8a"),
    ("Pixel 6a", "Android 14", "429dpi 429dpi 1080x2400", "arm64-v8a"),
    ("Pixel 7", "Android 14", "416dpi 416dpi 1080x2400", "arm64-v8a"),
    ("Pixel 7 Pro", "Android 14", "512dpi 512dpi 1440x3120", "arm64-v8a"),
    ("Pixel 8", "Android 14", "428dpi 428dpi 1080x2400", "arm64-v8a"),
    ("OnePlus NE2213", "Android 14", "525dpi 525dpi 1440x3216", "arm64-v8a"),
    ("OnePlus CPH2449", "Android 14", "451dpi 451dpi 1240x2772", "arm64-v8a"),
    ("realme RMX3085", "Android 13", "409dpi 409dpi 1080x2400", "arm64-v8a"),
    ("realme RMX3370", "Android 13", "409dpi 409dpi 1080x2400", "arm64-v8a"),
    ("realme RMX3630", "Android 13", "400dpi 400dpi 1080x2412", "arm64-v8a"),
    ("HUAWEI ELS-NX9", "Android 12", "441dpi 441dpi 1080x2340", "arm64-v8a"),
    ("HUAWEI VOG-L29", "Android 12", "398dpi 398dpi 1080x2340", "arm64-v8a"),
    ("HONOR RMO-NX1", "Android 13", "391dpi 391dpi 1080x2388", "arm64-v8a"),
    ("HONOR REA-NX9", "Android 13", "435dpi 435dpi 1200x2664", "arm64-v8a"),
)
LOCALE_TIMEZONES: tuple[tuple[str, str], ...] = (
    ("ru", "Europe/Moscow"),
    ("ru", "Europe/Kaliningrad"),
    ("ru", "Europe/Samara"),
    ("ru", "Asia/Yekaterinburg"),
    ("ru", "Asia/Omsk"),
    ("ru", "Asia/Novosibirsk"),
    ("ru", "Asia/Krasnoyarsk"),
    ("ru", "Asia/Irkutsk"),
    ("ru", "Asia/Yakutsk"),
    ("ru", "Asia/Vladivostok"),
)
WEB_APP_VERSION = "26.7.15"
WEB_SCREEN = "1080x1920 1.0x"

DEFAULT_WEB_HEADER_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
)

# PREFERRED_VERSION = [
#     version for version in APP_VERSIONS if version[1] >= MIN_PREFERRED_BUILD
# ]
# LEGACY_VERSIONS = [
#     version for version in APP_VERSIONS if version[1] < MIN_PREFERRED_BUILD
# ]
