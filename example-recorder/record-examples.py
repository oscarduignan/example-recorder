from mitmproxy import http, ctx
import json
import os
import re
import shutil
import subprocess
from ulid import ULID

output_dir = "./recorded-examples"
pages_dir = f"{output_dir}/pages"
files_dir = f"{output_dir}/files"

os.makedirs(pages_dir, exist_ok=True)
os.makedirs(files_dir, exist_ok=True)

def request(flow):
    # trigger by running `curl -X SHUTDOWN -x localhost:8008 localhost > recorded-examples.zip`
    if flow.request.method == "SHUTDOWN":
        subprocess.run("./assess-examples", shell=True)
        subprocess.run("./report-results",  shell=True)
        shutil.make_archive(output_dir, "zip", output_dir)
        with open(f"{output_dir}.zip", mode="rb") as output:
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
                # make all urls point to shared files folder
                re.sub(
                    r'(href|src)="/?',
                    r'\1="../../files/',
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
        file_path = os.path.join(
            files_dir,
            # make url schemes a folder in the path and remove query strings
            str(flow.request.pretty_url).replace("://", "/").split("?")[0],
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        try:
            with open(file_path, "xb") as response:
                # TODO fixup paths in CSS so they point to local files
                response.write(flow.response.content)
        except:
            print(f"Skipping {file_path}, already captured")
