#!/usr/bin/env python3
"""Дымовая проверка тестового окружения Notes.

Пример:
    smoke.py --url http://127.0.0.1 --host pr-12.test.local --expect-version 1.0.0
Код возврата 0 - все проверки пройдены, 1 - есть ошибки.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request


def call(base, host, method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(base + path, data=data, method=method)
    request.add_header("Host", host)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            body = response.read()
            return response.status, (json.loads(body) if body else None)
    except urllib.error.HTTPError as error:
        return error.code, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="адрес Traefik, например http://127.0.0.1")
    parser.add_argument("--host", required=True, help="имя хоста окружения")
    parser.add_argument("--expect-version", help="ожидаемая версия API")
    args = parser.parse_args()

    failures = []

    def check(title, condition):
        print(("OK   " if condition else "FAIL ") + title)
        if not condition:
            failures.append(title)

    status, body = call(args.url, args.host, "GET", "/api/health")
    check("GET /api/health -> 200 ok", status == 200 and body == {"status": "ok"})

    status, body = call(args.url, args.host, "GET", "/api/version")
    check("GET /api/version -> 200", status == 200)
    if args.expect_version and body:
        check("версия API = " + args.expect_version, body.get("version") == args.expect_version)

    status, body = call(args.url, args.host, "POST", "/api/notes", {"text": "smoke"})
    check("POST /api/notes -> 201", status == 201)
    note_id = body["id"] if body else None

    status, body = call(args.url, args.host, "GET", "/api/notes")
    check("созданная заметка видна в списке", status == 200 and any(n["id"] == note_id for n in body or []))

    status, _ = call(args.url, args.host, "DELETE", "/api/notes/%s" % note_id)
    check("DELETE /api/notes/<id> -> 204", status == 204)

    print("Итог: %s" % ("все проверки пройдены" if not failures else "ошибок: %d" % len(failures)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
