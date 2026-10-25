
"""LLMShield command-line client."""

import argparse
import json
import sys

import requests

DEFAULT_API = "http://127.0.0.1:8000"


def main():
    parser = argparse.ArgumentParser(
        prog="llmshield",
        description="LLMShield LLM security testing CLI",
    )
    parser.add_argument(
        "--api",
        default=DEFAULT_API,
        help=f"Backend URL (default: {DEFAULT_API})",
    )

    commands = parser.add_subparsers(
        dest="command",
        required=True,
    )
    commands.add_parser("health", help="Check API status")
    commands.add_parser("scan", help="Run security tests")

    chat = commands.add_parser("chat", help="Chat with the configured model")
    chat.add_argument("message", help="Message to send")

    args = parser.parse_args()
    base = args.api.rstrip("/")

    try:
        if args.command == "health":
            response = requests.get(f"{base}/health", timeout=5)

        elif args.command == "scan":
            response = requests.post(f"{base}/scan", timeout=180)

        else:
            response = requests.post(
                f"{base}/chat",
                json={"message": args.message},
                timeout=100,
            )

        response.raise_for_status()
        data = response.json()

        if args.command == "chat":
            print(f"Provider: {data['provider']}")
            if data.get("demo_mode"):
                print("Mode: intentionally vulnerable demo")
            print(f"\n{data['reply']}")
            return

        if args.command == "health":
            print(json.dumps(data, indent=2))
            return

        print(f"\n{data['tool']} Security Scan")
        print(f"Provider: {data['provider']}")
        print("-" * 45)

        for result in data["results"]:
            print(
                f"[{result['status']}] "
                f"{result['id']} - {result['category']}"
            )
            print(f"  Evidence: {result['evidence']}")

        print("\nSummary")
        print(json.dumps(data["summary"], indent=2))

        # A non-zero exit code indicates a detected test failure.
        if data["summary"]["failed"] > 0:
            sys.exit(1)

        if data["summary"]["errors"] > 0:
            sys.exit(2)

    except requests.RequestException as exc:
        print(
            f"Request failed: {exc}\n"
            "Check that the LLMShield API is running.",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
