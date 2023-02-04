from mitmproxy import http, ctx
import json
import os
import re
import shutil
from ulid import ULID

pages_dir = "./captured-examples/pages"
static_dir = "./captured-examples/static"

os.makedirs(pages_dir, exist_ok=True)
os.makedirs(static_dir, exist_ok=True)


def request(flow):
    # trigger by running `curl -X SHUTDOWN -x localhost:8008 localhost > captured-examples.zip`
    if flow.request.method == "SHUTDOWN":
        shutil.make_archive("./captured-examples", "zip", "./captured-examples")
        with open("./captured-examples.zip", mode="rb") as output:
            body = output.read()
            size = str(len(body))
            flow.response = http.Response.make(
                200,
                body,
                {
                    "Content-Type": "application/zip, application/octet-stream",
                    "Content-Length": size,
                },
            )
            ctx.master.shutdown()


def response(flow):
    if (
        "Content-Type" in flow.response.headers
        and flow.response.headers["Content-Type"].find("text/html") != -1
    ):
        page_dir = os.path.join(pages_dir, str(ULID()))
        os.mkdir(page_dir)
        with open(
            os.path.join(page_dir, "metadata.json"), "w", encoding="utf-8"
        ) as metadata:
            metadata.write(
                json.dumps(
                    {
                        "request": {
                            "url": str(flow.request.pretty_url),
                            "headers": dict(flow.request.headers.items()),
                            "method": str(flow.request.method),
                        },
                        "response": {
                            "status_code": str(flow.response.status_code),
                            "headers": dict(flow.response.headers.items()),
                        },
                    },
                    indent=2,
                )
            )
        with open(
            os.path.join(page_dir, "index.html"), "w", encoding="utf-8"
        ) as response:
            # TODO fixup page relative paths
            # TODO fixup scheme relative paths "//"
            response.write(
                # make all urls point to shared static folder
                re.sub(
                    r'(href|src)="/?',
                    r'\1="../../static/',
                    # add scheme and domain to root relative paths
                    re.sub(
                        r'(href|src)="/([^/])',
                        rf'\1="{flow.request.scheme}/{flow.request.pretty_host}/\2',
                        # make url schemes a folder in the path
                        flow.response.text.replace("://", "/"),
                        flags=re.IGNORECASE,
                    ),
                    flags=re.IGNORECASE,
                )
            )
    else:
        static_file = os.path.join(
            static_dir,
            # make url schemes a folder in the path and remove query strings
            str(flow.request.pretty_url).replace("://", "/").split("?")[0],
        )
        os.makedirs(os.path.dirname(static_file), exist_ok=True)
        try:
            with open(static_file, "xb") as response:
                # TODO fixup paths in CSS so they point to local files
                response.write(flow.response.content)
        except:
            print(f"Skipping {static_file}, already captured")
