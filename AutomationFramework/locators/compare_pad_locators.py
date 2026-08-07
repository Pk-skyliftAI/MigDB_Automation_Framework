class ComparePadLocators:

    # ComparePad is a separate backend service this environment can't
    # reach - live 2026-08-06 both "Configure" and "Monitor" sub-screens
    # show "Connection Failed / Unable to connect to ComparePad server."
    # with a "Retry Connection" button, confirmed as the expected state
    # here (not a bug to chase) - per user instruction, coverage only
    # confirms navigation lands on the right sub-item, not screen
    # content, since content is gated on that external service.

    CONFIGURE_ITEM = "Configure"
    MONITOR_ITEM_ID = "comparePadMonitor"
