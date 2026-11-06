# thai-lang-for-qwen

> กันอาการ **language bleed** — อักษรจีน/kana/Hangul และเครื่องหมาย full-width หลุดมาในข้อความภาษาไทยของ AI agent (model ตระกูล Qwen และ model ที่ train มากับข้อมูลภาษาจีนปริมาณมาก)

เช่น `或` หลุดมาแทน `หรือ`, หรือพิมพ์ `，：（）` แบบ full-width กลางประโยคไทย — เป็น artifact ของ model ไม่ใช่ตั้งใจ และ agent มักมองข้ามเอง skill นี้จึงสั่งให้ตรวจก่อนส่ง พร้อม linter สำหรับ file ยาว

## Features

- **Self-check เมื่อ agent เขียนภาษาไทย** — SKILL.md สอนตารางคู่หลุดบ่อย (`或→หรือ`, `的→ของ/ที่`, `，→,` ฯลฯ) ให้ agent ตรวจคำตอบก่อนส่ง
- **Linter script** (`scripts/check_bleed.py`) — ตรวจ file/deliverable ภาษาไทยแบบ deterministic: scan Unicode ต้องสงสัย (CJK U+4E00–U+9FFF, kana, Hangul, full-width U+FF00–U+FFEF) รายงาน `file:line:col` + codepoint + คำแนะนำแก้, exit 1 เมื่อพบ
- **ไม่ลบมั่ว** — script รายงานอย่างเดียว agent เป็นผู้ตัดสิน และรองรับ `--allow` สำหรับอักษรจีนที่ตั้งใจใช้ (คำแปล, ชื่อเฉพาะ, quoted source)
- **Style guide แนบใน skill** — คำทับศัพท์/ศัพท์เทคนิคให้เขียนเป็นอังกฤษ (linter, script, file, font...) ไม่ทับศัพท์เป็นไทย

## Install

ต้องให้มี Node.js ≥ 22.20 ในเครื่อง (สำหรับ npx) — ตัว script ใช้แค่ python3 ไม่มี dependency

```bash
# ติดตั้งจาก repo นี้ (รันในโฟลเดอร์ project ของคุณ)
npx skills add thanet-s/thai-lang-for-qwen-skill

# ใช้ทุก project (user-level)
npx skills add thanet-s/thai-lang-for-qwen-skill -g

# เลือก agent ที่ต้องการโดยตรง (เช่น zcode / claude-code / codex)
npx skills add thanet-s/thai-lang-for-qwen-skill --skill thai-lang-for-qwen -a zcode
```

CLI จะ detection agent ที่ติดตั้งในเครื่องแล้วเลือกตำแหน่งลงให้อัตโนมัติ (เช่น ZCode → `~/.zcode/skills/`, Claude Code → `~/.claude/skills/`) ดูตัวเลือกทั้งหมดด้วย `npx skills find` และ `npx skills list`

### Manual install

คัดลอกโฟลเดอร์ skill ไปวางใน discovery path ของ agent เอง:

```bash
git clone https://github.com/thanet-s/thai-lang-for-qwen-skill.git
cp -r thai-lang-for-qwen-skill/skills/thai-lang-for-qwen ~/.zcode/skills/   # ZCode (user scope)
# หรือลงระดับ project: cp -r ... <project>/.zcode/skills/
```

## Usage

- **อัตโนมัติ** — agent จะเรียกใช้ skill เองเมื่อเขียนข้อความภาษาไทยเนื้อหายาว หรือเมื่อคุณบ่นว่า "ไทยปนจีน" "ตัวจีนโผล่" (trigger จาก `description` ใน frontmatter)
- **บังคับเรียก** — พิมพ์ `/thai-lang-for-qwen` แล้วตามด้วยงาน เช่น `/thai-lang-for-qwen ช่วยร่างประกาศเป็นภาษาไทยทางการ`
- **รัน linter เอง** —

```bash
python3 -I skills/thai-lang-for-qwen/scripts/check_bleed.py draft.md
python3 -I skills/thai-lang-for-qwen/scripts/check_bleed.py --text "ทดสอบ 或 แล้ว，ผ่าน"
python3 -I skills/thai-lang-for-qwen/scripts/check_bleed.py th.md --allow 北京   # ตัวที่จงใจใช้
```

## Repo layout

```
thai-lang-for-qwen-skill/
├── README.md
└── skills/
    └── thai-lang-for-qwen/
        ├── SKILL.md                 ← ตัว skill (frontmatter + instructions)
        └── scripts/
            └── check_bleed.py       ← linter (stdlib only, exit 1 เมื่อพบ)
```

## Credits

Skill format และ CLI: [vercel-labs/skills](https://github.com/vercel-labs/skills) (`npx skills`) · รองรับทุก agent ที่อ่าน `SKILL.md` — ZCode, Claude Code, Codex, Cursor ฯลฯ
