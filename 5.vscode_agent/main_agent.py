import sys
import argparse

class VSCodeAgent:
    def __init__(self):
        self.status = "initialized"

    def start(self):
        print("🎉 VSCode Agent is running.")
        self.status = "running"
        self.do_some_work()

    def stop(self):
        print("🛑 VSCode Agent is stopping.")
        self.status = "stopped"

    def do_some_work(self):
        # Platzhalter für Hauptfunktionalität
        print("👩‍💻 Doing primary work...")

    def get_status(self):
        print(f"Status: {self.status}")

def argument_parser():
    parser = argparse.ArgumentParser(description="VSCode Agent Controller")
    parser.add_argument('--action', choices=['start', 'stop', 'status'], default='start', help="Aktion für den Agent")
    return parser.parse_args()

def main():
    args = argument_parser()
    agent = VSCodeAgent()

    if args.action == 'start':
        agent.start()
    elif args.action == 'stop':
        agent.stop()
    elif args.action == 'status':
        agent.get_status()
    else:
        print("Unbekannte Aktion.")
        sys.exit(1)

if __name__ == "__main__":
    main()
