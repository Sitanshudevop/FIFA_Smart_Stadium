import re

with open('backend/api/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import asyncio
if 'import asyncio' not in content:
    content = content.replace('import logging', 'import asyncio\nimport logging')

# Replace orchestrator calls
def patch_orchestrator(func_name, fallback_msg):
    global content
    
    # regex for `result: dict[str, Any] = await orchestrator.func_name(...)`
    # replacing it with asyncio.wait_for block
    old_code_pattern = rf'(result: dict\[str, Any\] = await orchestrator\.{func_name}\([^)]*\))'
    
    def replacer(match):
        old = match.group(1)
        return f'result: dict[str, Any] = await asyncio.wait_for({old.replace("result: dict[str, Any] = ", "")}, timeout=4.0)'
    
    content = re.sub(old_code_pattern, replacer, content)

patch_orchestrator('process_incident', 'Incident processing degraded.')
patch_orchestrator('assist_fan', 'Fan assist degraded.')

# Replace GenAI native calls (vision, simulation, dispatch)
old_genai = r'(response = await (?:orchestrator\._client|client)\.aio\.models\.generate_content\((?:.|\n)*?\))'
def replacer_genai(match):
    old = match.group(1)
    if 'asyncio.wait_for' not in old:
        return f'response = await asyncio.wait_for({old.replace("response = await ", "")}, timeout=4.0)'
    return old

content = re.sub(old_genai, replacer_genai, content)

# Add except asyncio.TimeoutError blocks to all endpoints
# We look for `except HTTPException:` and insert `except asyncio.TimeoutError:` before it
timeout_block = """
    except asyncio.TimeoutError:
        logger.warning("GenAI API timeout (4.0s). Entering degraded performance mode.")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "degraded_performance",
                "warning": "High network congestion detected. Operating on static offline fallbacks.",
                "message": "System is currently unable to reach the AI engine.",
            }
        )
    except HTTPException:"""

content = content.replace('    except HTTPException:', timeout_block.lstrip('\n'))

with open('backend/api/routes.py', 'w', encoding='utf-8') as f:
    f.write(content)
