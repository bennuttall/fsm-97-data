# FSM 97 — Video Files

## Format

The game's video files use EA's proprietary **TGQ** format (`.TGQ` extension), also known
as EA TGQ or EABT. The container uses EA's chunk format, identifiable by the `SCHl` magic
bytes at the start of each file.

- **Video codec**: TGQ (EA proprietary, lossy, block-based)
- **Audio codec**: ADPCM EA (EA's variant of IMA ADPCM)
- **Resolution**: 320×208
- **Frame rate**: 15 fps
- **Audio**: 22050 Hz, stereo

`ffmpeg` can decode these files natively using the `ea` demuxer:

```bash
ffmpeg -i INPUT.TGQ -c:v libx264 -c:a aac OUTPUT.mp4
```

No third-party tools or special flags required. Note that `ffprobe` reports `Duration: N/A`
on the raw `.TGQ` files — duration is only available after transcoding.

---

## Files

All 8 `.TGQ` files are in the `fmv/` subdirectory of the game install. All files are
dated 7 April 1997.

| File         | Size  | Duration | Converted                     | Description                  |
|--------------|-------|----------|-------------------------------|------------------------------|
| FSMINTRO.TGQ | 9.5MB | 36s      | `videos/fsmintro.mp4`  | Title intro sequence         |
| CREDITS.TGQ  | 23MB  | ~88s     | `videos/credits.mp4`   | End credits (exit game)      |
| LWIN.TGQ     | 6.2MB | 20s      | `videos/lwin.mp4`      | League win cutscene          |
| PROM.TGQ     | 6.5MB | 21s      | `videos/prom.mp4`      | Promotion cutscene           |
| REL.TGQ      | 5.9MB | 18s      | `videos/rel.mp4`       | Relegation cutscene          |
| CUPW.TGQ     | 4.7MB | 15s      | `videos/cupw.mp4`      | Cup win cutscene             |
| CUPL.TGQ     | 4.4MB | 14s      | `videos/cupl.mp4`      | Cup loss cutscene            |
| SACKED.TGQ   | 4.0MB | 15s      | `videos/sacked.mp4`    | Manager sacked cutscene      |

---

## Visual Style

All cutscenes share the same aesthetic: real-world live-action football footage,
heavily tinted blue/purple, with overlaid title text in a typewriter-style font.
The footage appears to come from mid-1990s football broadcasts and press events.
A "SPORTSELECTRONIC" brand/sponsor is visible in some clips.

---

## Video Descriptions

### FSMINTRO.TGQ — Title Intro (36s)

Plays on game startup. Opens with animated EA logo (bold red geometric shapes on black).
Transitions to blue-tinted live-action football footage with evocative single-word
overlays fading in and out:

- **"Faszination"** (German — "Fascination") — blurred close-up of players
- **"Passion"** — manager/coach figure
- **"Victory"** — goalkeeper diving at goal
- Closes on crowd/press-event footage outside what appears to be a sports retail outlet

The German word "Faszination" reflects the game's European origin (published by EA in
Germany/Europe).

---

### CREDITS.TGQ — End Credits (~88s)

Plays when the player exits the game. The longest video at 23MB.

Dark background with animated overlays: flickering C/C++ source code snippets (actual
game code — function names like `LPMatch`, `m_check`, `PostponeMatchesWithSha` are
visible), bug tracker screenshots (project "FSM-PCCD", entries dated 02/09/96), design
sketches, and oscilloscope/RGB colour-picker graphics.

Each person's name appears large in the foreground, with their role in smaller text above
it. Small inset thumbnails show childhood/baby photos of each staff member.

Full credits (in order of appearance):

| Role                   | Name               |
|------------------------|--------------------|
| Executive Producer     | Bruce McMillan     |
| Associate Producer     | John Mathieu       |
| Assistant Producer     | Mark Bergan        |
| Concept & Game Design  | Jon Law            |
| Lead Programmer        | Dave Colclough     |
| (programming)          | Chris Adams        |
| (programming)          | David Burton       |
| (programming)          | Robin Green        |
| (programming)          | Chris Wood         |
| Additional Programming | Miguel Melo        |
| Front End Art          | Justin Rae         |
| Stadium Art            | Andy Johns         |
| (art)                  | Catherine Harris   |
| Video Art              | Jason Lord         |
| Video Programming      | Martin Griffiths   |
| Audio Producer         | Chris Nicholls     |
| Audio Programming      | Nick Laviers       |
| Music                  | James Hannigan     |
| Sound Effects          | Bill Lusty         |
| (QA/testing)           | Adelle Kellett     |
| Technical Specialist   | David Burton       |
| Player Database Design | Darren King        |
| Test Manager           | Matt Price         |
| Lead Tester            | Darren King        |
| (tester)               | Lawrence Doyle     |
| (tester)               | Julian Glover      |
| (tester)               | Darren Tuckey      |
| Documentation          | James Lenoel       |
| Marketing              | Margaret Murray    |
| Production             | Julie Pain         |
| QA Lead                | Chris Chaplin      |
| QA Tester              | Dominic Murphy     |
| Special Thanks         | Kevin Buckner      |
| Special Thanks         | Danny Isaac        |
| Special Thanks         | Neil Cook          |
| Special Thanks         | Jules Burt         |
| Special Thanks         | Matt Eyre          |
| Special Thanks         | Marco Mele         |

The final seconds show a heavily glitched/distorted frame — likely an intentional
artistic fade-out effect.

---

### LWIN.TGQ — League Win (20s)

Blue-tinted celebration footage: players embracing (shirt number 14 visible), followed by
what appears to be a manager or club official celebrating at a press/sponsor event
(SPORTSELECTRONIC branding visible in background). Euphoric atmosphere.

---

### PROM.TGQ — Promotion (21s)

Blue-tinted celebration footage. Title text: **"Uppflyttning"** (Swedish for "Promotion").
Shows a player celebrating with arms raised, followed by a close-up of a ball on grass.

The Swedish word suggests the video files are shared across language versions of the game,
with title text baked into the video rather than dynamically generated.

---

### REL.TGQ — Relegation (18s)

Blue-tinted footage. Title text: **"Relegation"**. Centrepiece is a man in the stands,
head thrown back, expression of anguish — a visceral reaction to defeat. Suits the
emotional weight of the scenario.

---

### CUPW.TGQ — Cup Win (15s)

Blue-tinted trophy celebration footage. Text overlay reads **"Campeon de Copa"** (Spanish,
"Cup Champion") and **"Campioni"** (Italian, "Champions"). Players embracing around a
trophy.

---

### CUPL.TGQ — Cup Loss (14s)

Blue-tinted footage of feet/boots on the pitch, followed by a man raising an arm.
Text overlays: **"Finaliste de"** (French, "Finalist of") and **"Subcampeón de copa"**
(Spanish, "Cup runner-up"). Subdued compared to CUPW.

---

### SACKED.TGQ — Manager Sacked (15s)

Blue-tinted close-up of two people, one in a football shirt. Title text: **"Sacked"**.
Appropriately bleak.

---

## Language Notes

The cutscene text is baked into the video files rather than generated in-engine. The mix
of languages (German, Swedish, Spanish, French, Italian, English) across different files
suggests either:

- The same video assets were shipped for all regional editions, and each region happened
  to get one language in the title overlay, or
- The footage was licensed from various European sources and the title cards reflect the
  origin of each clip

The intro's use of "Faszination" (German) aligns with the game being developed/published
by EA's European operation.

---

## Extraction Notes

The `vcr/` subdirectory in the game install is empty. All video content is in `fmv/`.

Conversion command:
```bash
ffmpeg -i INPUT.TGQ -c:v libx264 -c:a aac OUTPUT.mp4
```

Frame extraction command (1 fps):
```bash
ffmpeg -i OUTPUT.mp4 -vf fps=1 frames/frame_%04d.png
```

Extracted frames are stored in `frames/<name>/`.
