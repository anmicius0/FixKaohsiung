import os
from dataclasses import dataclass
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

PROJECT_ROOT: str = os.getenv("PROJECT_ROOT", "/Users/anmicius/Projects/FixKaohsiung")
GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
ACCEPTED_CITY: str = "高雄市"
INPUT_DIR: str = os.path.join(PROJECT_ROOT, "data/original")
PROCESSED_DIR: str = os.path.join(PROJECT_ROOT, "data/processed")


POLICE_DICT: Dict[str, int] = {
    "左營區": 9,
    "楠梓區": 13,
    "三民區": 1,
    "鼓山區": 8,
    "鹽埕區": 5,
    "前金區": 6,
    "新興區": 4,
    "苓雅區": 10,
    "前鎮區": 11,
    "小港區": 12,
    "旗津區": 42,
    "鳳山區": 14,
    "大寮區": 19,
    "林園區": 20,
    "仁武區": 15,
    "大社區": 16,
    "岡山區": 21,
    "橋頭區": 23,
    "燕巢區": 25,
    "梓官區": 24,
    "鳥松區": 17,
    "大樹區": 18,
    "彌陀區": 26,
    "永安區": 27,
    "路竹區": 28,
    "湖內區": 29,
    "茄萣區": 30,
    "阿蓮區": 31,
    "田寮區": 32,
    "旗山區": 33,
    "美濃區": 34,
    "內門區": 35,
    "杉林區": 36,
    "甲仙區": 37,
    "六龜區": 38,
    "茂林區": 39,
    "桃源區": 40,
    "那瑪夏區": 41,
}

INCIDENT_LIST: List[Dict[str, str]] = [
    {
        "parent_value": "165",
        "child_value": "在人行道、行人穿越道違規停車。(但機車及騎樓不在此限)(56.1.1)",
        "child_text": """
        ✅ 在人行道、行人穿越道違規停車。(56.1.1)

        ✅ 駕駛人離車、熄火，已違反高雄市政府交通局“臨時停車”定義。因此判定為“停車”
        🔗 https://www.tbkc.gov.tw/Message/OtherInfo/Question?id=f4359355-c403-4bb9-8df8-fe4e05b400a9#:~:text=%E4%BE%9D%E6%93%9A%E9%81%93%E8%B7%AF%E4%BA%A4%E9%80%9A%E7%AE%A1%E7%90%86%E8%99%95%E7%BD%B0,%E4%BF%9D%E6%8C%81%E7%AB%8B%E5%8D%B3%E8%A1%8C%E9%A7%9B%E4%B9%8B%E7%8B%80%E6%85%8B%E3%80%82
        
        ✅ 根據高雄高等行政法院判例：駕駛人離車、熄火即足以判定為「停車」而非「臨時停車」
        🔗 https://lawsnote.com/judgement/67c002bcb135d37f6e826d05?t=731874857

        ✅ 時間不在深夜時段（0時至6時），因此不適用「違反道路交通管理事件統一裁罰基準及處理細則第12條施以勸導審核認定原則 」第六款施以勸導不舉發
        """,
    },
]


@dataclass
class ImapConfig:
    """IMAP configuration dataclass."""

    host: str
    port: int
    user: str
    password: str
    mailbox: str = "INBOX"

    @classmethod
    def from_env(cls) -> "ImapConfig":
        """Create configuration from environment variables."""
        return cls(
            host=os.getenv("IMAP_HOST", "disroot.org"),
            port=int(os.getenv("IMAP_PORT", "993")),
            user=os.getenv("IMAP_USER", "anmicius@disroot.org"),
            password=os.getenv("IMAP_PASSWORD", ""),
            mailbox=os.getenv("IMAP_MAILBOX", "INBOX"),
        )


@dataclass
class AppConfig:
    """Application configuration."""

    max_wait: int = 300
    wait_interval: int = 5
    verification_url: str = "https://policemail.kcg.gov.tw/VerifyLetter.aspx"
    subject_filter: str = "高雄市政府警察局警政信箱案件受理通知信"

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create configuration from environment variables."""
        return cls(
            max_wait=int(os.getenv("MAX_WAIT", "300")),
            wait_interval=int(os.getenv("WAIT_INTERVAL", "5")),
            verification_url=os.getenv(
                "VERIFICATION_URL", "https://policemail.kcg.gov.tw/VerifyLetter.aspx"
            ),
            subject_filter=os.getenv(
                "SUBJECT_FILTER", "高雄市政府警察局警政信箱案件受理通知信"
            ),
        )


IMAP_CONFIG: ImapConfig = ImapConfig.from_env()
APP_CONFIG: AppConfig = AppConfig.from_env()

# --- START OF FILE src/configs/constants.py ---

LICENCE_PROMPT = "Detected license plate: {}-{}. Is this correct? [Y/n]: "
LICENCE_PART_PROMPT = "The {} part of the license: "
LICENCE_INVALID_PROMPT = (
    "Must be at least 2 characters and contain only letters/numbers."
)
LICENCE_CONFIRM_PROMPT = "Entered license plate: {}-{}. Is this correct? [Y/n]: "
CATEGORY_PROMPT = (
    "Available incident categories:\n"
    + "{}"  # Placeholder for categories
    + "\nEnter the number of your choice: "
)
CONFIRM_PROMPT = "{}\nConfirm the data [Y/n]: "
