"""Example plugin: terminal bell when a run stops (harmless demo of the event API)."""
PLUGIN_INFO = {
    "name": "Beep On Stop",
    "version": "1.0",
    "author": "4R022",
    "description": "Rings the terminal bell and logs a message whenever clicking stops",
}


def register(api):
    def on_stop(payload):
        print("\a", end="", flush=True)
        api.log("stopped: " + str(payload.get("reason", "")))

    api.on("stop", on_stop)
