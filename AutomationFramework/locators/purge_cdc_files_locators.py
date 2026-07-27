class PurgeCdcFilesLocators:

    # Confirmed against a live aria snapshot of the Setup > Purge CDC
    # Files screen (2026-07-26).

    MANAGER_PARAMETERS_HEADING = ("heading", "MANAGER PARAMETERS")

    # These toggle checkboxes' real <input> is a zero-size element behind
    # a styled label.purge-toggle proxy (a different flavor of the usual
    # hidden-input-behind-a-styled-span trick) - Playwright correctly
    # reports the input itself as not visible, so visibility checks
    # target the visible label via its aria-label instead.
    ENABLE_PURGEOLDEXTRACTS_TOGGLE = (
        "label.purge-toggle[aria-label='Enable PURGEOLDEXTRACTS']"
    )

    ENABLE_AUTOSTART_TOGGLE = (
        "label.purge-toggle[aria-label='Enable AUTOSTART']"
    )

    ENABLE_AUTORESTART_TOGGLE = (
        "label.purge-toggle[aria-label='Enable AUTORESTART']"
    )

    # "Apply to mgr.prm" / "Reset" only render once at least one
    # parameter toggle is enabled - in the default (nothing enabled)
    # state this placeholder shows instead.
    NO_PARAMETER_ENABLED_TEXT = "enable a parameter block above"
