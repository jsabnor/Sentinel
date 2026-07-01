# Universal Accessibility Design

Sentinel is designed so ANYONE can use a computer, regardless of age, ability, or technical knowledge.

## Core Principles
- **Zero learning curve** — you speak, Sentinel acts. No commands to memorize.
- **Natural conversation** — talk like you would to a person.
- **Always helpful** — if something fails, explain why and offer alternatives.
- **Never intimidating** — no error codes, no technical jargon unless asked.
- **Proactive** — notice when the user seems stuck and offer help.

## User Profiles We Support

### Young Children (pre-readers)
- Simple vocabulary, short sentences
- Visual + audio feedback for every action
- Safety guardrails: can't delete, buy, or install without parent confirmation
- Fun, encouraging tone
- Can ask "what can I do?" to hear options

### Seniors / Non-technical users
- Patient, clear explanations
- Never assumes prior knowledge
- Confirms actions before executing
- Helps with common tasks: email, photos, video calls

### Visually Impaired Users
- EVERYTHING is spoken — no visual-only information
- Precise descriptions of what's happening
- Audio cues for state changes (listening, processing, done)
- Screen content can be read aloud

### Users with Motor Disabilities
- Fully voice-controlled — no keyboard or mouse needed
- Long press or single word activation
- Hands-free operation

### Users with Cognitive Disabilities
- One task at a time
- Simple, step-by-step guidance
- Repeat or rephrase if confused
- Visual + audio reinforcement

## Interaction Modes

### Mode 1: Guided (default for new users)
Agent introduces itself, asks what the user wants to do, guides step by step.
"Hi! I'm Sentinel. I can help you use your computer. What would you like to do?"

### Mode 2: Direct (for experienced users)
Short commands, minimal chit-chat. "Open Chrome", "What's the weather?"

### Mode 3: Tutorial
Agent teaches the user what it can do.
"You can ask me to: open programs, search the internet, read your emails, play music..."

## Safety by Default
- Children mode: no purchases, no deletions, no system changes
- Confirmation required for: installing software, changing settings, deleting files
- Emergency stop: say "stop", "cancel", "para" to abort any action
- Parent/guardian can configure allowed actions

## What We Need to Build

### Phase 1: Foundation (what we have + improvements)
- [x] Voice push-to-talk
- [x] Visual status indicator
- [x] Clean voice responses
- [ ] Wake word detection (porcupine/ openWakeWord) — *free, offline, reliable*
- [ ] Audio cues for state changes (beep when listening, done sound)
- [ ] "What can you do?" / "Ayuda" — agent lists capabilities

### Phase 2: Accessibility Features
- [ ] User profile selection (child, standard, expert)
- [ ] Simplified vocabulary for children
- [ ] Parent/guardian controls
- [ ] Screen reader integration (NVDA/JAWS on Windows)
- [ ] High contrast indicator mode
- [ ] Adjustable speech speed
- [ ] Multi-language on-the-fly switching

### Phase 3: Proactive Intelligence
- [ ] Context awareness — knows what app is open
- [ ] Suggests next actions
- [ ] Notices errors and offers to fix
- [ ] Learns user preferences over time

### Phase 4: Ecosystem
- [ ] Installer for non-technical users (one-click)
- [ ] Auto-update
- [ ] Community knowledge base
- [ ] Multi-device sync

## Immediate Next Steps (what we can do now)

1. **Add audio cues** — short beeps/chimes for: started listening, processing, done
2. **Add wake word** — use openWakeWord (free, offline, reliable, multi-language)
3. **Improve voice responses** — teach the LLM to speak simply for children mode
4. **Add "help" knowledge** — what to say when user says "help" or "what can you do"
5. **Safety profiles** — child mode with restricted actions
6. **Onboarding flow** — first-time user gets an introduction
