from dataclasses import dataclass
from typing import Dict, Tuple

# from src.utils.location import get_address
from src.data_handling.input import get_jpeg_paths
from src.utils.ui import clean_input
from src.data_handling.processing import get_datetime, licence_recognition
from src.config import POLICE_DICT
from src.utils.ui import status_print, StatusLevel


@dataclass
class PersonalInfo:
    name: str
    ssn: str
    home_address: str
    email: str
    phone: str


@dataclass
class ReportData:
    licence_first: str
    licence_second: str
    incident_datetime: str
    vehicle_type: str
    incident_address: Dict[str, str]
    police_station: str
    complaint_description: str
    category_parent: str
    category_child: str


# Constants
EMPTY_ADDRESS = {
    "formatted_address": "804 高雄市鼓山區美術東三路108號",
    "neighborhood": "美術東三路108號",
    "district": "鼓山區",
    "city": "高雄市",
}


personal_info = PersonalInfo(
    name="林紹恆",
    ssn="F131411459",
    home_address="804107高雄市鼓山區美術東六街127號11樓",
    email="u41j7u18@addy.io",
    phone="0968761803",
)

report_data = ReportData(
    incident_datetime="",
    incident_address=EMPTY_ADDRESS,
    police_station="",
    licence_first="",
    licence_second="",
    category_parent="165",
    category_child="在人行道、行人穿越道違規停車。(但機車及騎樓不在此限)(56.1.1)",
    complaint_description="""
        ✅ 在人行道、行人穿越道違規停車。(56.1.1)

        ✅ 駕駛人離車、熄火，已違反高雄市政府交通局"臨時停車"定義。因此判定為"停車"
        🔗 https://www.tbkc.gov.tw/Message/OtherInfo/Question?id=f4359355-c403-4bb9-8df8-fe4e05b400a9#:~:text=%E4%BE%9D%E6%93%9A%E9%81%93%E8%B7%AF%E4%BA%A4%E9%80%9A%E7%AE%A1%E7%90%86%E8%99%95%E7%BD%B0,%E4%BF%9D%E6%8C%81%E7%AB%8B%E5%8D%B3%E8%A1%8C%E9%A7%9B%E4%B9%8B%E7%8B%80%E6%85%8B%E3%80%82
        
        ✅ 根據高雄高等行政法院判例：駕駛人離車、熄火即足以判定為「停車」而非「臨時停車」
        🔗 https://lawsnote.com/judgement/67c002bcb135d37f6e826d05?t=731874857

        ✅ 時間不在深夜時段（0時至6時），因此不適用「違反道路交通管理事件統一裁罰基準及處理細則第12條施以勸導審核認定原則 」第六款施以勸導不舉發
        """,
    vehicle_type="0",
)


def _prep_licence() -> None:
    """
    Prepare license plate data for the report.
    Tries OCR detection first, then falls back to manual input.
    """
    # Try automatic OCR detection
    try:
        ocr_result = licence_recognition()
        if ocr_result:
            licence_first, licence_second = ocr_result
            if clean_input(
                f"Detected license: {licence_first}-{licence_second}. Correct? [Y/n]: "
            ).lower() in ("y", ""):
                report_data.licence_first, report_data.licence_second = (
                    licence_first,
                    licence_second,
                )
                return
    except Exception:
        pass

    # Manual input fallback
    while True:
        report_data.licence_first = (
            clean_input("First part of license: ").strip().upper()
        )
        report_data.licence_second = (
            clean_input("Second part of license: ").strip().upper()
        )

        if (
            len(report_data.licence_first) >= 2
            and report_data.licence_first.isalnum()
            and len(report_data.licence_second) >= 2
            and report_data.licence_second.isalnum()
        ):
            if clean_input(
                f"License: {report_data.licence_first}-{report_data.licence_second}. Correct? [Y/n]: "
            ).lower() in ("y", ""):
                return
        else:
            print("License parts must be at least 2 alphanumeric characters.")


def _prep_confirm() -> bool:
    """
    Display a summary of all collected data and ask for confirmation.

    Creates a formatted summary of both personal information and report data,
    then asks the user to confirm if the information is correct.

    Returns:
        bool: True if user confirms the data, None otherwise.
    """
    summary = (
        f"Report Data Summary:\nLicense Plate: {report_data.licence_first}-{report_data.licence_second}\n"
        f"Incident Time: {report_data.incident_datetime or 'Not available'}\n"
        + "\n".join(
            f"  {k}: {v or 'Not available'}"
            for k, v in report_data.incident_address.items()
        )
        + f"\nPolice Station: {report_data.police_station or 'Not available'}\n"
    )
    confirm = clean_input(f"{summary} \nConfirm the data [Y/n]: ").strip().lower()
    return confirm in ("y", "")


def prepare_data() -> Tuple[PersonalInfo, ReportData]:
    """
    Prepare report data by gathering information from image and user input.
    """
    status_print("Collecting incident information...", StatusLevel.INFO)
    try:
        img_path = get_jpeg_paths()[0]
        report_data.incident_datetime = get_datetime(img_path)

        # report_data.incident_address = get_address(img_path)
        report_data.police_station = str(
            POLICE_DICT[report_data.incident_address["district"]]
        )

        _prep_licence()

        if _prep_confirm():
            status_print("Report data confirmed", StatusLevel.SUCCESS)
            return personal_info, report_data
    except Exception as e:
        status_print(f"Error preparing data: {e}", StatusLevel.ERROR)
        raise ValueError(f"Error preparing data: {e}")
