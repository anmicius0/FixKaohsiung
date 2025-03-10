from src.data_handling.processing import preprocess_img
from src.data_handling.schemas import prepare_data
from src.core.procedure import auto_report
from src.utils.ui import status_print, StatusLevel
from src.utils.mail import process_email
from src.data_handling.output import clear_IO


def kaohsiung_auto_report() -> None:
    try:
        status_print("Starting automated report process", StatusLevel.INFO)

        # Let the functions handle their own status messages
        preprocess_img()
        (personal_info, report_data) = prepare_data()
        auto_report(personal_info, report_data)
        process_email()
        clear_IO()

        status_print("Report process completed successfully!", StatusLevel.SUCCESS)
    except Exception as e:
        status_print(f"Error in reporting process: {e}", StatusLevel.ERROR)
