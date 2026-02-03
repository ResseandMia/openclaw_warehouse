---
name: ad-prompt-generator
description: Analyze competitor ads and generate brand-specific prompts for Nano Banana. Use when user provides competitor ad image and wants to create a prompt for their own product.
---

# Ad Prompt Generator

Analyze competitor ad creatives and generate Nano Banana prompts adapted to brand identity.

## Workflow

### Step 1: Get Competitor Ad Image
User provides competitor ad image (screenshot/photo).

### Step 2: Analyze the Ad
Perform visual + copy teardown:

**Visual Analysis:**
- Layout structure
- Primary focal point
- Secondary elements
- Visual flow (eye movement)
- Color palette (estimate hex codes)
- Font styles (serif/sans/handwritten/bold)
- Image style (UGC/studio/lifestyle/product-only/minimalist/cinematic)
- Use of contrast, whitespace, framing, overlays

**Copy Analysis:**
- Extract all visible text
- Identify: Hook, Core promise, CTA
- Classify psychological angle:
  - Pain relief
  - Fear/urgency
  - Status/identity
  - Curiosity
  - Ease/simplicity
  - Authority/credibility

### Step 3: Retrieve Brand Context
Read brand documents from Feishu folder to extract:
- Brand colors (hex codes)
- Brand voice & tone
- Target demographic
- Product positioning
- Visual constraints or preferences

### Step 4: Generate Nano Banana Prompt

**Required Format:**
```
[Subject / Action] + [Art Style / Medium] + [Lighting / Atmosphere] + [Camera / Angle] + [Composition & Layout Details] + [Brand Color Instructions] + [Product Representation Instructions] + [Specific Text Requirement: "Exact text" in "Font style"] + [Clarity & Legibility Constraints] --ar [Aspect Ratio]
```

**Text Accuracy Rules:**
- Specify exact text strings
- Specify font style (bold, clean sans-serif, condensed)
- Specify placement (top, center, badge, overlay)
- Include instructions to avoid distorted/incorrect text

### Step 5: Output

**Format:**
```markdown
## Analysis

- Why the competitor ad works
- Psychological angle
- Structural effectiveness

## Nano Banana Prompt

```
[Full prompt here]
```

## Key Elements Preserved
- [List elements kept from competitor ad]
```

## Trigger
- User sends competitor ad image
- User says: "生成 prompt" / "create prompt" / "分析这个广告"
