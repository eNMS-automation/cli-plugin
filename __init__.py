from flask import request, render_template, Blueprint


class Plugin:
    def __init__(self, server, controller, db, **kwargs):
        @server.cli.command(name="run_service")
        @argument("name")
        @option("--devices")
        @option("--payload")
        def start(name, devices, payload):
            devices_list = devices.split(",") if devices else []
            devices_list = [db.fetch("device", name=name).id for name in devices_list]
            payload_dict = loads(payload) if payload else {}
            payload_dict.update(devices=devices_list, trigger="CLI", creator=getuser())
            service = db.fetch("service", name=name)
            results = app.run(service.id, **payload_dict)
            db.session.commit()
            echo(app.str_dict(results))

        @server.cli.command(name="delete_log")
        @option(
            "--keep-last-days", default=15, help="Number of days to keep",
        )
        @option(
            "--log",
            "-l",
            required=True,
            type=Choice(("changelog", "result")),
            help="Type of logs",
        )
        def delete_log(keep_last_days, log):
            deletion_time = datetime.now() - timedelta(days=keep_last_days)
            app.result_log_deletion(
                date_time=deletion_time.strftime("%d/%m/%Y %H:%M:%S"),
                deletion_types=[log],
            )
            app.log("info", f"deleted all logs in '{log}' up until {deletion_time}")