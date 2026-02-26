# Translation Presets

Predefined style configurations by genre. Each preset fills default values into `style.md` and provides a base pronoun/honorific table for `characters.md`.

User selects a preset during Phase 0. The preset is saved to `project.md` and can be overridden at any time by editing context files directly.

---

## Preset: tu_tien_co_phong

**Name**: Tu tiên — Cổ phong
**Genre**: 修仙 / 仙侠 (cultivation, immortal hero)
**Feel**: Trang trọng, cổ kính, giữ nhiều Hán Việt

### Pronoun defaults

| Relationship | Speaker → Listener | Default |
|---|---|---|
| Self (male, neutral) | — | ta |
| Self (male, humble) | — | tại hạ |
| Self (female, neutral) | — | ta |
| Self (female, gentle) | — | thiếp |
| Peer male → peer male | friendly | huynh / đệ |
| Peer male → peer male | hostile | ngươi |
| Peer female → peer male | friendly | sư huynh / công tử |
| Male → female (peer) | friendly | sư muội / cô nương |
| Male → female (lover) | intimate | nàng |
| Female → male (lover) | intimate | chàng |
| Senior → junior | — | ngươi / đồ nhi / tiểu tử |
| Junior → senior | respectful | tiền bối / sư phụ / lão nhân gia |
| Master → disciple | — | đồ nhi / con |
| Disciple → master | — | sư phụ / thầy |
| Emperor/king → subject | — | khanh / ngươi |
| Subject → emperor | — | bệ hạ / hoàng thượng |
| Enemy → enemy | — | ngươi / tên kia / lão tặc |
| Narration: he | — | hắn / y |
| Narration: she | — | nàng / thị |

### Vocabulary register

- Prose: văn phong trang trọng, nhiều từ Hán Việt
- Keep Hán Việt for: cultivation terms (tu luyện, đan điền, linh lực, kiếm khí...), titles, place names
- Combat descriptions: chi tiết, hùng tráng, dùng từ cổ (kiếm quang, chưởng phong, huyết quang...)
- Inner monologue: vẫn giữ giọng cổ phong
- Idioms (成语): dịch Hán Việt, giữ nguyên nếu phổ biến (ví dụ: thiên hạ đệ nhất)

### Narration style

- Third person omniscient
- Formal, measured pacing
- Description-heavy for scenery and combat

---

## Preset: tu_tien_hien_dai

**Name**: Tu tiên — Hiện đại hóa
**Genre**: 修仙 nhưng giọng văn gần gũi hơn
**Feel**: Pha trộn cổ phong và hiện đại, dễ đọc, vẫn giữ "không khí" tu tiên

### Pronoun defaults

| Relationship | Speaker → Listener | Default |
|---|---|---|
| Self (male, neutral) | — | ta (trong chiến đấu/formal), tôi (nội tâm) |
| Self (female, neutral) | — | ta / tôi tuỳ ngữ cảnh |
| Peer male → peer male | friendly | huynh / anh (thân) |
| Peer male → peer male | hostile | ngươi / anh (lạnh) |
| Male → female (peer) | friendly | cô / sư muội |
| Male → female (lover) | intimate | em / nàng (lúc nghiêm túc) |
| Female → male (lover) | intimate | anh / chàng (lúc nghiêm túc) |
| Senior → junior | — | cậu / ngươi (tuỳ mood) |
| Junior → senior | respectful | tiền bối / sư phụ |
| Enemy → enemy | — | ngươi / anh / cậu (tuỳ mức thù) |
| Narration: he | — | hắn (stranger/enemy), anh ta (neutral), gã (negative) |
| Narration: she | — | nàng (positive), cô ta (neutral), thị (negative) |

### Vocabulary register

- Prose: trộn Hán Việt và thuần Việt, ưu tiên dễ hiểu
- Keep Hán Việt for: core cultivation terms only
- Combat: vẫn chi tiết nhưng dùng từ hiện đại hơn
- Inner monologue: hiện đại, có thể hơi tự sự
- Idioms: dịch nghĩa thuần Việt khi có thể, giữ Hán Việt khi nổi tiếng

### Narration style

- Third person, đôi khi limited (bám theo nhân vật chính)
- Nhịp nhanh hơn cổ phong
- Xen kẽ mô tả và hành động

---

## Preset: kiem_hiep

**Name**: Kiếm hiệp cổ điển
**Genre**: 武侠 (wuxia / martial arts)
**Feel**: Phong cách Kim Dung, Cổ Long — hào sảng, giang hồ, tình nghĩa

### Pronoun defaults

| Relationship | Speaker → Listener | Default |
|---|---|---|
| Self (male) | — | tại hạ / ta |
| Self (female) | — | tiểu muội / ta |
| Peer male → peer male | friendly | huynh đài / các hạ |
| Peer male → peer male | sworn brothers | đại ca / nhị đệ... |
| Male → female | respectful | cô nương / tiểu thư |
| Male → female | lover | nàng |
| Female → male | lover | chàng / lang quân |
| Senior → junior | — | tiểu hữu / tiểu tử (hostile) |
| Junior → senior | — | tiền bối / lão tiền bối |
| Stranger → stranger | polite | các hạ / huynh đài |
| Enemy | — | ngươi / tên giặc / lão tặc |
| Narration: he | — | hắn / chàng (protagonist) |
| Narration: she | — | nàng / thiếu nữ |

### Vocabulary register

- Prose: đậm chất giang hồ, trọng nghĩa khí
- Key terms: giang hồ, võ lâm, nội công, khinh công, ám khí, huyệt đạo...
- Combat: tiết tấu nhanh, miêu tả chiêu thức rõ ràng
- Food/drink: thường xuất hiện — dịch giữ vị Trung Hoa (nữ nhi hồng, hoa điêu...)
- Poetry: dịch thơ giữ vần, hoặc dịch thoát ý kèm chú thích

### Narration style

- Third person omniscient, đôi khi chuyển POV giữa nhân vật
- Miêu tả phong cảnh trữ tình
- Nhịp chậm lúc tâm tình, nhanh lúc giao đấu

---

## Preset: do_thi_than_mat

**Name**: Đô thị — Thân mật
**Genre**: 都市 (urban / modern)
**Feel**: Hiện đại, gần gũi, anh-em, tự nhiên

### Pronoun defaults

| Relationship | Speaker → Listener | Default |
|---|---|---|
| Self (male) | — | tôi / anh (với nữ) |
| Self (female) | — | tôi / em (với nam thân) |
| Male → male | friendly | cậu / ông (bạn bè) |
| Male → male | formal | anh / ông |
| Male → female | friendly | em / cô (chưa thân) |
| Female → male | friendly | anh |
| Couple | — | anh / em |
| Boss → employee | — | cậu / anh-chị |
| Employee → boss | — | sếp / giám đốc / anh-chị |
| Parent → child | — | con |
| Child → parent | — | bố-mẹ / ba-má |
| Enemy/rival | — | anh / cậu (mỉa mai), tên này (nội tâm) |
| Narration: he | — | anh ta / hắn (negative) / gã (casual negative) |
| Narration: she | — | cô ta / cô ấy / ả (negative) |

### Vocabulary register

- Prose: thuần Việt, đời thường, tự nhiên
- Không dùng Hán Việt trừ tên riêng
- Slang / internet language: chuyển sang tương đương tiếng Việt
- Brand names, tech terms: giữ nguyên hoặc phiên âm
- Inner monologue: rất tự nhiên, có thể dùng tiếng lóng

### Narration style

- First person hoặc third person limited
- Nhịp nhanh, đối thoại nhiều
- Mô tả ngắn gọn, ít thơ mộng

---

## Preset: do_thi_lanh_lung

**Name**: Đô thị — Lạnh lùng / Quyền lực
**Genre**: 都市 power fantasy, tổng tài, trùm mafia...
**Feel**: Sắc lạnh, quyền uy, khoảng cách

### Pronoun defaults

| Relationship | Speaker → Listener | Default |
|---|---|---|
| Self (male protagonist) | — | ta (power moments), tôi (bình thường) |
| Self (female lead) | — | tôi |
| Protagonist → subordinate | — | ngươi / cậu |
| Subordinate → protagonist | — | sếp / ông chủ / thiếu gia |
| Protagonist → female lead | early | cô |
| Protagonist → female lead | later | em |
| Female lead → protagonist | early | anh / ông ta (nội tâm) |
| Rival → protagonist | — | cậu (giả lịch sự) / tên kia (hostile) |
| Narration: he (protagonist) | — | hắn / anh ta |
| Narration: she | — | cô / cô ta |

### Vocabulary register

- Prose: sắc nét, ngắn gọn, đôi khi lạnh
- Business terms: giữ tiếng Anh nếu phổ biến (CEO, deal, meeting...)
- Power dynamics rõ ràng qua ngôn ngữ
- Action scenes: nhanh, gọn, bạo lực realism

### Narration style

- Third person, camera theo protagonist
- Câu ngắn, ít mô tả dài
- Nhấn mạnh áp lực, aura, power gap

---

## Preset: custom

**Name**: Custom
**Genre**: User-defined

Khi user chọn Custom:
1. Ask for genre/tone description
2. Ask for pronoun preferences (show example from closest preset)
3. Ask for vocabulary register preference
4. Generate style.md from answers

User can also start from any preset and modify specific fields.

---

## How presets are applied

During Phase 0, after chapter detection:

1. Auto-detect genre from first few chapters (look for cultivation terms, modern settings, martial arts...)
2. Suggest matching preset with example pronouns
3. User confirms or picks different preset
4. Preset fills:
   - `style.md` → vocabulary register, narration style, term handling rules
   - `characters.md` → default pronoun table header (actual character entries added during bootstrap)
5. Save chosen preset name to `project.md`

During processing, the context files (not the preset) are the source of truth. Presets are only used for initialization — after that, user edits to context files take priority.