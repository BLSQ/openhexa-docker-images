import os

if "HEXA_RUN_ID" in os.environ:
    try:
        from openhexa.utils import install_default_user_agent

        install_default_user_agent()
    except Exception:  # noqa: BLE001, S110 - never break interpreter startup
        pass
