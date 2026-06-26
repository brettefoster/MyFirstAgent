# Reasoning/Thinking Process Delimiter Research

## Overview

This document researches the standard delimiters and structural patterns used in AI model reasoning/thinking processes (often exposed via `reasoning_content`, `thinking`, or similar fields). Understanding these patterns enables proper parsing and formatting of internal model thought processes.

## Common Thinking Delimiter Patterns by Provider

### 0. Qwen (Qwen2.5, Qwen3, Qwen3.6)

Qwen models use a distinctive structured thinking format with markdown-based delimiters:

```
Thinking Process:

1.  **Deconstruct the request:**
    *   Topic: Programming.
    *   Form: Haiku (5-7-5 syllables).

2.  **Brainstorming themes/imagery related to programming:**

3.  **Drafting lines (aiming for 5-7-5):**
    *   *Attempt 1:*
        *   Code writes itself now (5)
    *   *Attempt 2 (Classic bug focus):*
        *   Search for missing semicolon (7)
    *   *Option A:* Final polished version
    *   *Option B:* Alternative approach

4.  **Final Selection:**
    *   I'll go with a variation of Attempt 2.

5.  **Output Generation:**
    Search for hidden bug,
```

**Pattern:** `Thinking Process:` header followed by numbered sections with bold titles
**Common internal markers within thinking:**
- `Thinking Process:` - Top-level header marking the start of reasoning
- `N.  **<section title>:**` - Section headers (bold, numbered)
- `*   *Attempt N:*` - Attempt iteration markers
- `*   *Attempt N (<description>):*` - Attempt markers with optional description
- `*   *Option X:*` - Option comparison markers
- `*   *Option X (<description>):*` - Option markers with optional description
- `->` - Used for self-correction notes (e.g., `-> Fail.`, `-> Fix:`)

**Variants:** `<thinking>...</thinking>` (less common in Qwen, more common in other models)

**Key observation:** Qwen's thinking format is highly structured with consistent markdown formatting, making it particularly amenable to regex-based parsing.

---

### 1. OpenAI (o1, o3-series, GPT-4o with reasoning)

OpenAI uses the `<thinking>` XML tag as the standard delimiter:

```xml
<thinking>
Let me think about this step by step...
1. First, I need to understand the request...
2. Then, I'll consider the options...
</thinking>
```

**Pattern:** `<thinking>...</thinking>`
**Variants:** `<reasoning>...</reasoning>`, `<Thought>...</Thought>` (older format)

### 2. Anthropic (Claude)

Claude uses the `<thinking>` tag as well, often with nested structure:

```xml
<thinking>
Let me break this down:

Step 1: Understand the problem
Step 2: Explore solutions
Step 3: Evaluate and conclude
</thinking>
```

**Pattern:** `<thinking>...</thinking>`
**Common internal markers within thinking:**
- `## Step N:` or `### Step N:` (markdown headings)
- `Attempt N:` (when iterating on solutions)
- `Option A/B/C:` (when comparing alternatives)
- `Wait,` or `Hmm,` (self-correction markers)

### 3. Google (Gemini)

Gemini often uses structured reasoning with markdown:

```markdown
Let me think through this:

1. **First**, I need to...
2. **Next**, I should...
3. **Finally**, I can...

Alternative approaches:
- Option 1: ...
- Option 2: ...
```

**Pattern:** Numbered lists with bold labels, `Option N:` markers
**Variants:** `Thought:`, `Reasoning:`, `Analysis:`

### 4. Open-source Models (Llama, Mistral, etc.)

Open-source models vary widely but common patterns include:

```
<thought>...</thought>
<reasoning>...</reasoning>
<thinking_process>...</thinking_process>
```

**Common internal markers:**
- `Let me think...`
- `First,` / `Second,` / `Finally,`
- `Wait,` (self-correction)
- `Actually,` (self-correction)

## Observed Patterns from Sample Data

From the sample thinking process analyzed in this project:

```
Thinking Process:

1.  **Deconstruct the request:**
    *   Topic: Programming.
    *   Form: Haiku (5-7-5 syllables).

2.  **Brainstorming themes/imagery related to programming:**

3.  **Drafting lines (aiming for 5-7-5):**
    *   *Attempt 1:*
    *   *Attempt 2 (Classic bug focus):*
    *   *Option A:*
    *   *Option B:*

4.  **Final Selection:**

5.  **Output Generation:**
```

### Identified Delimiter Patterns:

| Pattern | Example | Frequency | Reliability |
|---------|---------|-----------|-------------|
| `Attempt N:` | `*   *Attempt 1:*` | High in drafting sections | **High** - unique to reasoning |
| `Option X:` | `*   *Option A:*` | Medium in selection sections | **High** - unique to reasoning |
| `N. **...**:` | `1.  **Deconstruct the request:**` | High as section headers | Medium - could appear elsewhere |
| `Thinking Process:` | `Thinking Process:` | Low - only at top level | **High** - but only once |

## Recommendations

### Primary Delimiter: `Attempt N:`
- **Most reliable** for marking distinct iteration boundaries
- Format: `Attempt <number>[(<description>)]:`
- Example regex: `\*?\s*\*?Attempt\s+\d+[\w\s\(\)]*?:\*?`
- Unique to reasoning processes (won't appear in normal responses)

### Secondary Delimiter: `Option X:`
- Useful for marking alternative choices in selection phases
- Format: `Option <letter>:`
- Example regex: `\*?\s*\*?Option\s+[A-Z]\s*[:\*]\*?`

### Tertiary Delimiter: Numbered Step Headers
- Useful for top-level section organization
- Format: `<number>. **<text>:**`
- Less reliable as a standalone delimiter since it could appear in non-reasoning content

## Inline ANSI Highlighting Approach

### Design Principle
Delimiters are highlighted by injecting ANSI color codes directly into the text stream, **preserving all original whitespace, newlines, and indentation**. Only the delimiter text itself is wrapped in color codes - nothing else is reformatted.

### Visual Hierarchy (inline coloring)

| Element | ANSI Style | Terminal Effect |
|---------|-----------|-----------------|
| `Thinking Process:` | BOLD + BRIGHT_WHITE + BG_BLUE | White text on blue background header |
| `N. **Section Title:**` | BRIGHT_CYAN + BOLD | Bold cyan section headers |
| `*   *Attempt N:*` | BRIGHT_BLACK + BG_BRIGHT_YELLOW + BOLD | Black text on yellow background bar |
| `*   *Attempt N (desc):*` | BRIGHT_BLACK + BG_BRIGHT_YELLOW (bold only on number) | Bold number, normal description, same background |
| `*   *Option X:*` | BRIGHT_MAGENTA + BOLD | Bold magenta option markers |
| `-> Fail.` / `-> Fix:` | BRIGHT_RED + DIM | Dim red self-correction notes |

### Regex Patterns for Inline Matching

```python
_ATTEMPT_RE = re.compile(r'(\*?\s*\*?Attempt\s+\d+[\w\s\(\)]*?:\*?)')
_OPTION_RE = re.compile(r'(\*?\s*\*?Option\s+[A-Z]\s*[:\*]\*?)')
_SECTION_RE = re.compile(r'^(\s*\d+\.\s*\*\*[^*]+\*\*:)', re.MULTILINE)
_CORRECTION_RE = re.compile(r'(->\s+\S+[\s.]*)')
```

### How It Works
1. Input is a raw string (all newlines, indentation preserved)
2. Each regex finds delimiter matches and wraps them in ANSI color codes
3. Output is the same string with ANSI codes injected at delimiter points
4. `NO_COLOR` environment variable strips all colors for clean output

### Example

**Input (raw):**
```
Thinking Process:

1.  **Deconstruct the request:**
    *   *Attempt 1:*
        *   Code writes itself now (5)
    *   *Attempt 2 (Classic bug focus):*
        *   Works at last, I smile (5) -> Fail.
```

**Output (with ANSI codes injected):**
```
[WHITE+BOLD+BG_BLUE]Thinking Process:[RESET]

[CYAN+BOLD]1.  **Deconstruct the request:**[RESET]
    *   [BLACK+BG_YELLOW+BOLD]*   *Attempt 1:*[RESET]
        *   Code writes itself now (5)
    *   [BLACK+BG_YELLOW+BOLD]*   *Attempt 2[RESET][BLACK+BG_YELLOW]* (Classic bug focus):*[RESET]
        *   Works at last, I smile (5) [RED+DIM]-> Fail.[RESET]
```

## References

- OpenAI API Documentation: `<thinking>` tag usage
- Anthropic Claude Documentation: `<thinking>` tag usage
- Various open-source model prompting guides