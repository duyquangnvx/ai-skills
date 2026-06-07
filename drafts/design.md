# webnovel-studio — Design

> Tài liệu thiết kế chốt cho CLI sản xuất audiobook (và sau này video) từ webnovel. Chốt mô hình khái
> niệm + các quyết định kiến trúc nền tảng; "vì sao" chi tiết của từng quyết định nên promote dần sang
> `docs/decisions.md` (ADR) khi vào implement. Bối cảnh TTS: xem `docs/omnivoice.md`.

## 0. Nguyên tắc đã chốt

1. **Filesystem = Source of Truth.** Mọi thứ là file phẳng, diff được bằng git. Trạng thái dẫn xuất
   (compiled) tách riêng, dựng lại được bất cứ lúc nào.
2. **CLI command = Agent tool.** Một surface duy nhất, cùng một core. Agent gọi đúng bộ lệnh user gọi;
   khác biệt chỉ ở `--json`.
3. **Deterministic-first.** LLM/TTS chỉ chạy ở stage *cần suy luận*. Phần còn lại là code thuần,
   idempotent, cache được. Re-render chương cũ luôn ra cùng kết quả.
4. **Context LLM không phụ thuộc kích thước truyện.** Phần "toàn cục" nằm ở code (alias index); LLM chỉ
   thấy cast nhỏ của riêng một chương — đúng ở scale 3000–4000 chương, hàng trăm–nghìn nhân vật.
5. **Bất biến nhất quán giọng.** Segment chỉ trỏ tới *persona*, **không bao giờ** trỏ thẳng voice. Voice
   được *resolve* lúc render từ persona + timeline danh tính. Mọi thay đổi giọng (lộ danh tính, rebind,
   upgrade preset) chỉ cần **re-render**, không sửa tay segment.

## 1. Năm quyết định nền tảng

| # | Vấn đề | Chốt |
|---|---|---|
| 1 | OmniVoice chạy thế nào | **batch-CLI** (`omnivoice-infer-batch` + `test.jsonl`) sau một **TTS provider interface** |
| 2 | Nhất quán giọng | **Khóa MỘT voiceprint WAV → mọi synth là CLONE từ đó** (design ≠ synth) |
| 3 | Mô hình voice-identity | **3 lớp Entity / Persona / Voice** + timeline event + Effect layer (DSP) |
| 4 | Scale | candidate set **dẫn bởi text** qua **alias-index period-scoped**, two-pass attribution |
| 5 | Orchestration | DAG deterministic mặc định + Agent ở stage suy luận + agent-mode escape hatch |

## 2. Mô hình voice-identity (lõi)

Gốc của vấn đề: "nhân vật → giọng" gộp nhầm hai trục độc lập.

- **Identity continuity** — *ai thật sự là ai* (linh hồn/thực thể, xuyên suốt).
- **Presentation** — *họ nghe ra sao với người nghe* tại thời điểm này.

→ Tách thành 3 lớp lưu trữ + 2 cơ chế động:

| Lớp / cơ chế | Là gì |
|---|---|
| **Entity** | Linh hồn/thực thể, ID bền, mang `lineage` (trùng sinh) + `trueVoice` (giọng thật). 1:1 với persona cho nhân vật thường (auto-tạo). |
| **Persona** | "Mặt nạ" được trình hiện: có nhiều alias, giữ MỘT voice. Là **đích attribution của segment**. Cải trang/giả nam-nữ/phân kỳ tuổi = persona mới của cùng entity. |
| **Voice** | Một **voiceprint đã khóa** (WAV reference) + metadata. Đơn vị synthesis. |
| **Timeline event** *(động)* | Chỉ cho ca *fronting/reveal* (đoạt xá) và *transform* (biến hình). Replay deterministic. |
| **Effect layer** *(động)* | Biến đổi giọng bằng **DSP hậu kỳ** (pitch/growl/reverb/filter), chồng lên output đã synth. |

### 2.1 Cơ chế nhất quán: Voiceprint Factory + Khóa (insight cốt lõi)

> Cả OmniVoice Design lẫn Gemini TTS **không nhất quán 100% giữa các lần gọi**. Cách duy nhất đảm bảo
> giọng nhất quán xuyên 4000 chương: **khóa MỘT mẫu audio rồi clone từ đó mãi mãi.**

Tách *nguồn tạo voiceprint* (design, chạy 1 lần/voice) khỏi *engine synthesis* (clone, chạy hàng triệu câu):

1. **Design đúng MỘT lần** bằng provider tùy chọn (xem §8) → ra mẫu reference WAV.
2. **Clone thử bằng OmniVoice → audition CHÍNH bản clone** (không phải mẫu gốc, vì timbre đã đi qua encoder
   OmniVoice). Đạt → **khóa** WAV làm voiceprint (SoT). Provider/instruct chỉ còn là *provenance metadata*.
3. **Mọi synthesis về sau = OmniVoice CLONE** với `ref_audio = voiceprint đã khóa`. **Không bao giờ** design
   lại lúc synth.
4. **Auto voice** chỉ dùng tạm cho entity chưa rõ; phải khóa trước khi render thật.

Kết hợp **content-addressed cache** (mỗi segment synth 1 lần rồi cache) → nhất quán ở **ba lớp**: voiceprint
khóa (xuyên nhân vật) + clone-from-fixed-ref + cache (xuyên lần chạy). `voiceprints/*.wav` là **SoT timbre,
giữ trong git qua git-lfs — KHÔNG gitignore.**

### 2.2 Resolve voice

```ts
function resolveVoice(personaId, at) {
  const p = persona(personaId)
  const base = p.voice ?? entity(p.entity).trueVoice          // voice của persona (mặc định = giọng thật entity)
  const front = latestEvent({ type: "front", bodyPersona: personaId, atOrBefore: at })
  let voice = base
  if (front) {
    const reveal = latestEvent({ type: "reveal", target: personaId, atOrBefore: at })
    if (reveal?.audienceKnows) {
      voice = reveal.onRevealVoice === "keep_body" ? base : entity(front.frontEntity).trueVoice
    } // else: hidden → giữ giọng thân (base)
  }
  return { voiceprint: voice.voiceprint, effect: activeEffects(personaId, at) }  // effect: từ transform events + segment FX
}
```

Ví dụ đoạt xá — cùng persona `per_trieu`, giọng tự đổi mà **không sửa segment nào**:

| Chương | Event hiệu lực | audienceKnows | → Voiceprint | Người nghe cảm nhận |
|---|---|---|---|---|
| 5 | (chưa có) | — | `voice_trieu` | Triệu Công Tử thật |
| 12 | `front` (Lâm Phong) | false | `voice_trieu` (thân) | nghe Triệu — *nhân vật trong truyện vẫn tưởng Triệu* |
| 88 | `reveal` (soul) | true | `voice_lamphong` | nghe Lâm Phong, công khai |

## 3. Taxonomy edge-case (tham chiếu khái niệm, KHÔNG phải schema)

Mọi tình huống "đổi giọng" quy về một trong sáu cơ chế; mỗi cơ chế gắn với một cách *biểu diễn* đã có sẵn —
primitive code vẫn nhỏ (entity/persona/voice/event + resolve + DSP). Bảng này để **phân loại ca mới**, không
sinh thêm code.

| # | Cơ chế | Ví dụ | Biểu diễn |
|---|---|---|---|
| **M1** | Entity mới + link huyết thống | trùng sinh, chuyển sinh, xuyên không, dung hợp | entity mới, `lineage.from`; persona/voice riêng mỗi kiếp; reveal là *narrative* (giọng không đổi). Tùy chọn "echo" = effect nhẹ. |
| **M2** | Tráo thực thể trong cùng thân (fronting) | đoạt xá, hoán hồn, phụ thể, quỷ nhập | `front` event + `audienceKnows` + `onRevealVoice`. Giọng thân → giọng entity-fronting khi reveal. |
| **M3** | Persona mới (cùng entity, trình hiện khác) | cải trang, giả nam/nữ, mạo danh, mặt nạ, phân kỳ tuổi | persona mới (voice riêng + alias period-scoped). Mạo danh = `persona.voice` trỏ voice của persona bị mạo (voice_alias). |
| **M4** | Biến đổi hình hài | thú/ma/rồng hình, hồi xuân/lão hóa, trọng thương/trúng độc | `transform` event → **DSP effect**, giữ voiceprint. Cần timbre khác hẳn → khóa voiceprint thứ 2, switch bằng event. |
| **M5** | Kênh truyền | truyền âm, thần thức, qua pháp bảo/khoảng cách, hệ thống trong đầu | **DSP effect** (segment hoặc transform), chồng được lên M4. |
| **M6** | KHÔNG đổi giọng — chỉ delivery | cảm xúc, say, mơ ngủ, hấp hối | mức **segment**: prosody + tag phi ngôn ngữ OmniVoice (`[laughter]`, `[sigh]`). Chốt chặn để model không phình. |

**Binding mặc định** (chiến lược gán, không phải "đổi"): entity vô giới/chưa lộ → *provisional voice*, rebind
sau; người dẫn truyện → voice cấp project (`persona: null`); NPC vô danh → pool giọng generic; quần thể đồng
thanh → layer hợp xướng.

## 4. Schema (filesystem SoT, nhiều file nhỏ keyed theo id)

`registry/entities/*.json`
```jsonc
{
  "id": "ent_lamphong",
  "kind": "human",                 // human | beast | spirit | system | collective | unknown
  "displayName": "Lâm Phong",
  "trueVoice": "voice_lamphong",   // giọng THẬT của linh hồn (dùng khi fronting + revealed)
  "lineage": { "type": "transmigration", "from": ["ent_modern_linfeng"], "audienceKnows": false } // M1; optional
}
```

`registry/personas/*.json`
```jsonc
{
  "id": "per_trieu",
  "entity": "ent_trieu",           // thân/mặt nạ này gốc thuộc entity nào
  "aliases": ["Triệu Công Tử", "Triệu thiếu gia", "công tử"],
  "voice": "voice_trieu",          // bỏ trống ⇒ mặc định = entity.trueVoice
  "ageStage": "youth"              // optional: child | youth | adult | elder
}
```

`registry/voices/*.json` — **không có instruct lúc synth; instruct chỉ là provenance**
```jsonc
{
  "id": "voice_trieu",
  "voiceprint": "voiceprints/voice_trieu.wav",   // SoT timbre đã KHÓA (git-lfs)
  "refText": "...",                               // transcript mẫu, giúp clone (optional)
  "provenance": { "designer": "gemini", "baseVoice": "Kore", "instruct": "male, youth, arrogant", "designLang": "vi" },
  "basedOn": "library:storio/young-male-arrogant@1.2" // optional, nếu pull preset
}
```

`registry/aliases.jsonl` — append-only, **period-scoped**, alias→persona (router scale, chỉ string)
```jsonl
{"alias":"Diệp Phàm","persona":"per_diepham","from":1,"to":null}
{"alias":"Diệp cô nương","persona":"per_diep_conuong","from":12,"to":50}   // tên cải trang → persona female
{"alias":"Kiếm Tổ","persona":"per_diepham","from":300,"to":null}          // đạo hiệu sau timeskip
```

`registry/timeline.jsonl` — append-only, rất nhỏ, luôn load toàn bộ; chỉ M2/M4/M5
```jsonl
{"id":"e1","at":12,"type":"front","bodyPersona":"per_trieu","frontEntity":"ent_lamphong","audienceKnows":false}
{"id":"e2","at":88,"type":"reveal","target":"per_trieu","audienceKnows":true,"onRevealVoice":"soul"}
{"id":"e3","at":120,"type":"transform","target":"per_lamphong","effect":[{"pitch":-4},{"growl":0.6}],"to":140}
```

`chapters/0012/segments.jsonl` — **không chứa voice**
```jsonc
{"i":1,"type":"dialogue","persona":"per_trieu","text":"Ngươi cũng xứng?","delivery":{"emotion":"khinh miệt","tags":["[scoff]"]}}
{"i":2,"type":"narration","persona":null,"text":"Hắn quay lưng bỏ đi."}   // persona null → giọng dẫn truyện
```

`chapters/0012/cast.jsonl` — phái sinh (resolve), rẻ, cache được
```jsonc
{"i":1,"voiceprint":"voiceprints/voice_trieu.wav","effect":[],"text":"Ngươi cũng xứng?","tags":["[scoff]"]}
```

## 5. Cây thư mục workspace

```
my-novel/                      # = project = workspace = repo (giống một repo developer)
├── .studio/
│   ├── config.json            # provider, llm baseURL, model, tts params, concurrency  (≈ .claude)
│   ├── cache/                 # content-addressed: enhanced/segments/audio — disposable
│   └── state.json             # con trỏ resume / tiến độ build
├── .env                       # API keys (gitignored)
├── .gitignore
├── project.json               # title, slug, description, author, language, narratorVoice, sourceUrl
├── registry/                  # SoT cho casting
│   ├── entities/*.json
│   ├── personas/*.json
│   ├── voices/*.json
│   ├── voiceprints/*.wav      # SoT timbre đã khóa — git-lfs, KHÔNG gitignore
│   ├── aliases.jsonl          # append-only, period-scoped
│   ├── timeline.jsonl         # append-only events
│   └── presets.lock           # preset library đã pull + version (pin)
├── voice-library/             # preset pull từ vendor, cache theo version
├── chapters/
│   └── 0012/
│       ├── source.txt         # ① import   (SoT gốc, KHÔNG sửa)
│       ├── enhanced.md        # ② enhance  (khử convert/MTL, nâng văn — phái sinh)
│       ├── segments.jsonl     # ③ segment  (gán persona, KHÔNG có voice)
│       ├── cast.jsonl         # ④ resolve  (phái sinh, rẻ)
│       ├── audio/seg-*.wav    # ⑤ synth    (cache theo hash)
│       ├── chapter.wav        # ⑥ stitch
│       └── meta.json          # hash + trạng thái từng stage (status SoT theo chương)
└── output/                    # ⑦ thumbnail, ⑧ video (roadmap)
```

`.studio/config.json` (rút gọn)
```jsonc
{
  "llm": { "provider": "...", "baseURL": "...", "model": "...", "enhanceModel": null, "attributionModel": null },
  "tts": {
    "synth":  { "vendor": "omnivoice", "deployment": "local", "baseURL": null, "format": "wav", "sampleRate": 24000 },
    "design": { "provider": "gemini", "model": "gemini-3.1-flash-tts-preview" }  // chỉ chạy 1 lần/voice
  },
  "scoping": { "activeWindow": 10 },   // CHỈ làm prior khử nhập nhằng, KHÔNG phải nguồn candidate
  "concurrency": 4
}
```

`.gitignore` mặc định: `.env`, `.studio/cache/`, `chapters/*/audio/`, `chapters/*/chapter.wav`, `output/`,
`voice-library/`. **Giữ trong git:** `registry/` (gồm `voiceprints/*.wav` qua git-lfs — SoT timbre, không
được mất), `project.json`, `.studio/config.json`, `chapters/*/source.txt`, `enhanced.md`, `segments.jsonl`,
`meta.json`.

## 6. Pipeline (build-system DAG)

| # | Stage | Input | Output | Re-run khi | LLM/TTS |
|---|---|---|---|---|---|
| ① | import | nguồn/clipboard | `source.txt` | nguồn đổi | — |
| ② | enhance | `source.txt` | `enhanced.md` | source / prompt đổi | LLM |
| ③a | discover | `enhanced.md` + alias-index | personas (known + draft mới) | enhanced đổi | LLM (chỉ mention lạ) |
| ③b | segment | `enhanced.md` + persona-cards + timeline | `segments.jsonl` | enhanced / cast đổi | LLM |
| ④ | resolve | `segments.jsonl` + timeline + voices | `cast.jsonl` | **timeline/voice đổi** | code |
| ⑤ | synth | `cast.jsonl` | `audio/seg-*.wav` | dòng cast đổi (hash) | TTS clone |
| ⑥ | stitch | `audio/seg-*.wav` | `chapter.wav` | seg wav đổi | code (ffmpeg) |
| ⑦ | thumbnail | `enhanced.md` | `output/NNNN/thumb.png` | (roadmap) | |
| ⑧ | video | `chapter.wav` (1..N) + ảnh | `output/video-*.mp4` | (roadmap) | |

- **Idempotent + cache theo content-hash:** `hash(input + config + promptVersion)`. Đổi prompt enhance →
  invalidate từ ② trở đi, không render lại cả truyện.
- **Invalidation đắt giá rẻ đi nhờ bất biến §0.5:** thêm `reveal`/rebind voice → chỉ invalidate **④⑤⑥**,
  không đụng ③ (segment trỏ persona, không trỏ voice). Stage ⑤ cache `seg-*.wav` theo
  `hash(text + resolvedVoiceprint + effect)` → chỉnh giọng một nhân vật chỉ re-synth đúng dòng của nhân vật
  đó, không phải 4000 chương.

## 7. Scale — không inject cả cast

Candidate set **dẫn bởi text** (tên xuất hiện trong chương), KHÔNG bởi recency — "window K chương" hỏng vì
callback xa sau hàng trăm chương là chuyện thường.

```
Pass 1 (LLM, rẻ):  đọc chương → trích surface mentions (chỉ chuỗi tên)
Code (deterministic): match mentions → alias-index period-scoped → cast nhỏ của chương
                      mention không khớp → hàng đợi "alias/persona mới" (chờ confirm)
Pass 2 (LLM):      attribution + coref, CHỈ với cast nhỏ đã match
                   + binding-state do resolver cấp cho chương này
```

- **alias-index** = SoT ánh xạ tên→persona, period-scoped ⇒ attribution **deterministic**, nhất quán chương
  12 hay 1200. LLM không quyết phần known.
- **persona-card** gọn (`id, aliases, 1 dòng trait`) — context chỉ phụ thuộc số nhân vật *trong chương*
  (một dúm tới vài chục), không phụ thuộc tổng cast.
- **Active-cast window** (mặc định K=10) **chỉ làm prior** khử nhập nhằng alias dùng chung ("sư huynh" →
  người đang active), KHÔNG phải nguồn candidate.
- **Đại từ** ("hắn", "nàng") → coref cục bộ trong cảnh, không cần cast toàn cục.
- **Xung đột alias** (một alias → nhiều persona cùng khoảng chương) → cảnh báo, **không tự đoán**.
- **Persona mới không chặn segment:** segment chỉ cần `persona_id`; voice giải ở ④ (provisional, rebind sau).

## 8. TTS integration

- OmniVoice = model open-source k2-fsa (**Apache-2.0**, ra 2026-03-31), chạy local (GPU/Apple Silicon, 24kHz)
  hoặc hosted REST (WaveSpeedAI, submit→poll→URL). **Tiếng Việt đã verify: Design & Clone đều tốt.**
- Tích hợp qua **batch-CLI**: stage ④ sinh `test.jsonl` cho cả chương → spawn `omnivoice-infer-batch` → đọc
  `results/*.wav`. Chi phí load model khấu hao trên cả batch. Đặt sau **TTS provider interface** để sau cắm
  vendor khác mà không sửa core. `tts.deployment = local | hosted` (adapter xử polling cho hosted).
- **Voiceprint Factory (pluggable designer)** — sinh reference WAV, chạy 1 lần/voice:

  | Provider | Mạnh ở | Ghi chú |
  |---|---|---|
  | **Gemini TTS** *(khuyến nghị)* | giọng giàu tính cách, đạo diễn bằng prompt + audio tags | 30 giọng nền × style; design space timbre hẹp |
  | **OmniVoice Design** | không gian thuộc tính rộng (gender/age/pitch/accent) | timbre đa dạng hơn nhưng kém "diễn" |
  | **Clip thật / human** | timbre độc nhất | cần mẫu sạch ~3–10s |

  Mặc định **Gemini design → OmniVoice clone-and-lock**: Gemini cho giọng nhân vật giàu tính cách (chạy 1 lần,
  chi phí không đáng kể), OmniVoice gánh synth khối lượng lớn (rẻ/self-host) và đảm bảo nhất quán. Clone
  **cross-lingual** → có thể design ở ngôn ngữ Gemini mạnh rồi đọc tiếng Việt bằng timbre đó (test accent trước).

- **Effect layer = DSP hậu kỳ** (ffmpeg/sox) áp sau khi có wav, cho M4/M5 — giữ voiceprint gốc. KHÔNG dùng
  instruct lúc synth (tránh trôi timbre; instruct cũng không làm được growl/distortion).

Dòng `test.jsonl` mẫu sau resolve (clone từ voiceprint đã khóa):
```json
{"id":"ch0012_seg0001","text":"Ngươi cũng xứng?","ref_audio":"voiceprints/voice_trieu.wav","language_id":"vi","speed":1.0}
```

## 9. CLI surface (đồng thời là Agent Tools)

Áp `cli-design`: noun-verb (resource-first), mọi lệnh hỗ trợ `--json`; stdout = kết quả, stderr = log/progress;
exit `0` thành công, non-zero thất bại (gate ở dưới → non-zero); xác nhận trước hành động phá hủy.

```
studio init                                  # scaffold workspace + chọn narrator voice

# Nội dung — DAG, idempotent, resume được (skip stage 'done' theo meta.json)
studio chapter import <url|file>
studio chapter build  <n|--range a-b> [--from-stage enhance|segment|...]
studio chapter render <n>

# Registry — casting
studio entity   add|list|show
studio persona  add|list|show
studio alias    add|resolve|list             # resolve = tra "<tên> @ ch.N"
studio timeline add|list

# Voice
studio voice    list|show|assign
studio voice    design <persona> [--designer gemini|omnivoice|clip] [--design-lang ...]
studio voice    distinctness [--threshold ...]   # cảnh báo voiceprint nghe quá giống (cast lớn)
studio cast     inspect <n>                   # giọng đã resolve của chương

# Kiểm tra & thư viện
studio validate <n|all>                       # casting-completeness gate (xem dưới)
studio library  list|pull <preset>|upgrade

# Escape hatch
studio agent "<task>"
```

**Casting-completeness gate** (`validate`, cũng chặn `render`) — check **deterministic**, không phải phán đoán
LLM, đảm bảo cứng yêu cầu #1: chặn nếu *còn segment dialogue chưa resolve được persona* **hoặc** *có persona
trong cast chưa có voice*. Fail → route sang agent/user, exit non-zero.

**Agent orchestration** — agent là orchestrator *tùy chọn* trên CLI hoàn chỉnh; agent-tool là façade thứ hai
trên cùng core. Agent gánh các bước *cần phán đoán*: `design_voice` (đọc trait → đề xuất voice spec),
review attribution low-confidence, và mạnh nhất `add_identity_event` (đọc chương, tự phát hiện đoạt xá/cải
trang/reveal → ghi timeline event) — thứ khiến hệ edge-case **tự populate** thay vì bookkeeping tay. Mọi ghi
vào SoT đều human-in-the-loop confirm.

## 10. Voice preset library

- Preset kiểu **vendor**: `library:<vendor>/<preset>@<version>`, mỗi preset **gói sẵn voiceprint đã khóa**
  (vì design không deterministic, preset phải kèm mẫu audio, không chỉ instruct).
- `library pull` copy voiceprint + metadata vào `registry/voices/` + `registry/voiceprints/`, pin vào
  `presets.lock`. `library upgrade` so version, hiển thị diff, cho phép re-pin — **không tự đổi** voiceprint
  đang dùng nếu chưa confirm (đổi voiceprint giữa truyện = phá nhất quán).

## 11. Roadmap

Các stage tương lai là **leaf downstream**, chỉ tiêu thụ `chapter.wav` + metadata, **không đụng** mô hình lõi:

- **Thumbnail (⑦):** sinh ảnh từ (tóm tắt chương + style project). `studio thumbnail <n>`.
- **Video (⑧):** mux ảnh tĩnh + audio đã ghép, flexible gộp 1..N chương → 1 video kèm chapter markers
  (ffmpeg concat các `chapter.wav` theo range + map ảnh theo timeline). `studio video <range> [--image ...]`.

## 12. Cố tình KHÔNG làm bây giờ (YAGNI)

- Embedding/vector retrieval cho mention (chỉ thêm khi đo được recall alias-index kém).
- Python sidecar giữ model nóng (batch-CLI đủ cho xử lý theo chương).
- Multi-vendor TTS (chỉ cần interface sẵn, impl OmniVoice trước).
- `onRevealVoice: "blend"` (cần DSP trộn 2 giọng — hoãn; trước mắt `soul | keep_body`).
- E2E / pipeline integration tests (theo `principles.md`: TDD ở core/domain, hoãn E2E).

## 13. Còn cần verify thực tế (không chốt được trên giấy)

1. **Gemini tiếng Việt** — design trực tiếp tiếng Việt có tự nhiên không; nếu không → cross-lingual clone
   (design ngôn ngữ khác → OmniVoice đọc tiếng Việt) và nghe thử accent.
2. **Biến thiên OmniVoice Clone** giữa các câu → nếu lớn thì cache mức câu + chuẩn hóa âm lượng/EQ hậu kỳ.
3. **Độ dài tối đa / chunking** mỗi request và cách nối mượt.
4. **Quota/throughput** nếu hosted cho batch hàng trăm chương → có thể nghiêng self-host OmniVoice.
5. Tên tham số `generate()` chính xác + danh sách đầy đủ tag phi ngôn ngữ (xem `docs/omnivoice.md`).
6. Cơ chế **download/import** chương (nguồn, bản quyền, định dạng) — chưa chốt.