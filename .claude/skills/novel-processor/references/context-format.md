# Context File Formats

These files live in `context/` and are read before every processing step. They grow as new chapters are processed.

---

## glossary.md

Purpose: Single source of truth for all Chinese→Vietnamese term translations. Prevents inconsistency across chapters.

Format:

```markdown
# Glossary

## Cultivation / Martial Arts
| Chinese | Vietnamese | Notes | First seen |
|---------|-----------|-------|------------|
| 筑基期 | Trúc Cơ kỳ | Foundation building stage | ch.1 |
| 元婴期 | Nguyên Anh kỳ | Nascent soul stage | ch.5 |
| 灵力 | linh lực | spiritual energy | ch.1 |

## Places
| Chinese | Vietnamese | Notes | First seen |
|---------|-----------|-------|------------|
| 天山 | Thiên Sơn | main sect location | ch.1 |
| 幽冥谷 | U Minh Cốc | forbidden valley | ch.12 |

## Items / Artifacts
| Chinese | Vietnamese | Notes | First seen |
|---------|-----------|-------|------------|
| 灵石 | linh thạch | currency unit | ch.1 |

## Titles / Ranks
| Chinese | Vietnamese | Notes | First seen |
|---------|-----------|-------|------------|
| 掌门 | chưởng môn | sect leader | ch.1 |
| 长老 | trưởng lão | elder | ch.1 |

## Other
| Chinese | Vietnamese | Notes | First seen |
|---------|-----------|-------|------------|
```

Rules:
- Group by category for quick lookup
- Notes column captures context that affects translation choice
- First seen helps trace when a decision was made
- If a term has multiple valid translations, pick one and note alternatives in Notes
- Once a translation is chosen, it does not change unless user explicitly requests

---

## characters.md

Purpose: Track all characters, their relationships, and critically — how they address each other (xưng hô). This is the most important file for Vietnamese translation quality.

Format:

```markdown
# Characters

## Main Characters

### Lâm Phong (林峰)
- **Role**: Protagonist
- **Gender**: Male
- **Age**: ~18 at start
- **Key traits**: determined, humble origin, genius cultivator
- **Affiliations**: Thiên Sơn sect → inner disciple
- **First seen**: ch.1

**Xưng hô (how others address / how he addresses):**
| With | He calls them | They call him | Context |
|------|-------------|---------------|---------|
| Sư phụ (master) | sư phụ / thầy | đồ nhi / Phong nhi | formal master-disciple |
| Tô Dao (sư muội) | sư muội / Tô Dao | sư huynh | same sect, she is junior |
| Enemies | ngươi / tên kia | tiểu tử / thằng nhóc | hostile encounters |
| Strangers | các hạ / huynh đài | thiếu hiệp / công tử | polite/formal |

### Tô Dao (苏瑶)
- **Role**: Female lead
- **Gender**: Female
- **Age**: ~17 at start
- **Key traits**: intelligent, sect leader's daughter
- **Affiliations**: Thiên Sơn sect → core disciple
- **First seen**: ch.3

**Xưng hô:**
| With | She calls them | They call her | Context |
|------|--------------|---------------|---------|
| Lâm Phong | sư huynh | sư muội / Tô Dao | friendly senior-junior |
| Her father | cha / phụ thân | Dao nhi | family |
| Outsiders | ta / thiếp | Tô cô nương | formal female address |

## Supporting Characters

### [character template]
- **Role**: 
- **Gender**: 
- **Key traits**: 
- **Affiliations**: 
- **First seen**: ch.N

**Xưng hô:**
| With | Calls them | Called by them | Context |
|------|-----------|---------------|---------|

## Relationship Map (text summary)

Lâm Phong → Tô Dao: đồng môn, gradually romantic
Lâm Phong → Trương trưởng lão: master-disciple (formal)
...
```

Rules:
- Xưng hô table is mandatory for every named character — this is what prevents translation inconsistency
- Xưng hô can evolve (enemies become allies, lovers break up) — note chapter where change happens
- For minor characters appearing once, a single line entry is enough (no full xưng hô table)
- Vietnamese pronouns (ta, ngươi, hắn, y, nàng, thiếp...) must be tracked here

---

## style.md

Purpose: Lock in translation and writing style decisions so every chapter feels consistent.

Format:

```markdown
# Style Guide

## Genre & Tone
- Genre: tiên hiệp / huyền huyễn / võ hiệp / đô thị / etc.
- Tone: serious epic / light comedy / dark / mixed
- Era feel: cổ đại (ancient) / hiện đại / mixed

## Translation Conventions
- Chinese idioms (成语): translate meaning, keep original in parentheses for well-known ones
- Poetry/verses in text: translate with Vietnamese poetic structure, note original
- Measurement units: convert to Vietnamese equivalents or keep Chinese terms?
- Sound effects / onomatopoeia: adapt to Vietnamese equivalents

## Prose Style
- Register: văn ngôn (classical) / bạch thoại (modern) / mixed
- Narration voice: third person omniscient / limited / first person
- Paragraph length preference: match original / shorter for readability
- Dialogue style: use Vietnamese speech markers (—) or quotation marks ("")

## Terms to KEEP in Chinese (pinyin/Hán Việt)
- Example: 江湖 → giang hồ (keep as-is, well-known term)
- Example: 氣 → khí (keep Hán Việt reading)

## Terms to TRANSLATE to Vietnamese
- Example: 飞剑 → phi kiếm (Hán Việt) NOT "thanh kiếm bay"
- Example: 丹田 → đan điền (keep Hán Việt, standard term)

## Decided patterns
| Decision | Choice | Reason | Chapter |
|----------|--------|--------|---------|
| How to render 修炼 | tu luyện | standard Hán Việt | ch.1 |
| Combat description style | detailed, cinematic | matches original tone | ch.2 |
| Internal monologue format | italic, first person | distinguish from narration | ch.1 |
```

Rules:
- Every non-obvious translation decision gets recorded here
- "Decided patterns" table grows over time — it's the decision log
- When in doubt during processing, check this file first before making new decisions
- User can override any decision — update the file accordingly