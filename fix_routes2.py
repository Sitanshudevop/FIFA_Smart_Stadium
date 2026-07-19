with open('backend/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix )), timeout=4.0)\n        )
content = content.replace(")), timeout=4.0)\n        )", "), timeout=4.0)")

with open('backend/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
