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

    # Confirmed intentional (2026-08-10, user-verified): the screen's
    # default state changed. "Apply to mgr.prm" / "Reset" and the
    # mgr.prm syntax preview now render unconditionally, even with no
    # parameter toggle enabled - the old "enable a parameter block
    # above" placeholder text no longer appears at all.
    MGR_PRM_PREVIEW_TEXT = "mgr.prm"

    APPLY_BUTTON = ("button", "Apply to mgr.prm")

    RESET_BUTTON = ("button", "Reset")
