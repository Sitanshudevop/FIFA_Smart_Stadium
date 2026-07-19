import re
with open('backend/schemas/payload.py', 'r', encoding='utf-8') as f:
    c = f.read()

# Add AccessibilityFlags definition at the top of schemas
acc_flags = """
class AccessibilityFlags(BaseModel):
    high_contrast: bool = False
    enlarged_text: bool = False
    auto_tts_active: bool = False
    simplified_view: bool = False

"""
if 'class AccessibilityFlags' not in c:
    c = c.replace('class TaskAssignmentLLM(BaseModel):', acc_flags + 'class TaskAssignmentLLM(BaseModel):')

def inject_field(schema_name, field_def):
    pattern = rf"(class {schema_name}\(BaseModel\):[\s\S]*?)(?=\n\nclass |\n\n#|$)"
    def repl(m):
        block = m.group(1)
        if field_def.split(':')[0].strip() not in block:
            return block.rstrip() + "\n    " + field_def + "\n"
        return block
    return re.sub(pattern, repl, c)

c = inject_field('TaskAssignmentLLM', 'accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")')
c = inject_field('FanAssistLLM', 'accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")')
c = inject_field('VisionNavigateLLM', 'accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")')
c = inject_field('TaskAssignment', 'accessibility_flags: Optional[AccessibilityFlags] = None')
c = inject_field('FanAssistResponse', 'accessibility_flags: Optional[AccessibilityFlags] = None')
c = inject_field('VisionNavigateResponse', 'accessibility_flags: Optional[AccessibilityFlags] = None')
c = inject_field('DispatchResolutionLLM', 'accessibility_flags: AccessibilityFlags = Field(description="Dynamic accessibility adjustments based on user context.")')
c = inject_field('DispatchResponse', 'accessibility_flags: Optional[AccessibilityFlags] = None')

with open('backend/schemas/payload.py', 'w', encoding='utf-8') as f:
    f.write(c)
