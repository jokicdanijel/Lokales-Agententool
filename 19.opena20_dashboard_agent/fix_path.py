with open("main.py") as f:
    content = f.read()

# Fix the root path - should be parent, not parent.parent.parent
content = content.replace("self.root = Path(__file__).parent.parent.parent", "self.root = Path(__file__).parent")

with open("main.py", "w") as f:
    f.write(content)

print("✅ Path fixed!")
