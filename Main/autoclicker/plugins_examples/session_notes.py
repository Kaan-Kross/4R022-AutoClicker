"""Example plugin: appends a one-line summary of every finished session to a text file."""
PLUGIN_INFO = {
    "name": "Session Notes",
    "version": "1.0",
    "author": "4R022",
    "description": "Writes a one-line summary of each finished session to session_notes.txt",
}


def register(api):
    def on_session(rec):
        line = "{started_at} | {total_clicks} clicks | {avg_cps} avg CPS | {stop_reason}\n".format(**rec)
        with open(api.data_dir / "session_notes.txt", "a", encoding="utf-8") as fh:
            fh.write(line)
        api.log("session note saved")

    api.on("session", on_session)
