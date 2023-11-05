from __future__ import annotations

import argparse
import json
from typing import Any

import requests

import extruct
from extruct import SYNTAXES


def metadata_from_url(
    url: str,
    syntaxes: list[str] = SYNTAXES,
    uniform: bool = False,
    schema_context: str = "http://schema.org",
    errors: str = "strict",
) -> dict[str, Any]:
    resp = requests.get(url, timeout=30)
    result: dict[str, Any] = {
        "url": url,
        "status": "{} {}".format(resp.status_code, resp.reason),
    }
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        return result
    result.update(
        extruct.extract(
            resp.content,
            base_url=url,  # FIXME: use base url
            syntaxes=syntaxes,
            uniform=uniform,
            schema_context=schema_context,
            errors=errors,
        )
    )
    return result


def main(args: Any | None = None) -> Any:
    parser = argparse.ArgumentParser(prog="extruct", description=__doc__)
    arg = parser.add_argument
    arg("url", help="The target URL")
    arg(
        "--syntaxes",
        nargs="+",
        choices=SYNTAXES,
        default=SYNTAXES,
        help="List of syntaxes to extract. Valid values any or all (default):"
        "microdata, opengraph, microformat json-ld, rdfa."
        "Example: --syntaxes microdata opengraph json-ld",
    )
    arg(
        "--uniform",
        default=False,
        help="""If True uniform output format of all syntaxes to a list of dicts.
                Returned dicts structure:
                {'@context': 'http://example.com',
                 '@type': 'example_type',
                 /* All other the properties in keys here */
                 }""",
    )
    arg(
        "--schema_context",
        default="http://schema.org",
        help="schema's context for current page",
    )
    arg(
        "--errors",
        default="log",
        choices=["strict", "log", "ignore"],
        help="errors: set to 'log'(default) to log the exceptions, 'ignore' to ignore"
        " them or 'strict' to raise them",
    )
    arg(
        "--stdout",
        default=False,
        help="""If True print the metadata to standard output.
        Otherwise the metadata is printed to standard error.
        """,
        action="store_true"
    )
    args = parser.parse_args(args)
    metadata = metadata_from_url(
        args.url, args.syntaxes, args.uniform, args.schema_context, args.errors
    )

    metadata_json = json.dumps(metadata, indent=2, sort_keys=True)
    if args.stdout:
        print(metadata_json)
        return ""
    else:
        return metadata_json
