# Session Management

## How Sessions Work
- Each time Sentinel starts, a new session is created automatically.
- Sessions are saved automatically when you exit.
- Session names are timestamps: `20260701-143052`.
- You can list and restore previous sessions.

## Session Commands (via Tools)
- `session_list` — Shows the last 5 saved sessions. Use limit parameter for more.
- `session_load` — Restores a session by name. The conversation continues from where it left off.

## Voice Commands for Sessions
When the user says things like:
- "Recupera la sesion anterior" → Call session_list first to show available sessions
- "Restaura la sesion de ayer" → Call session_list, find the matching session, call session_load
- "Que sesiones tengo guardadas?" → Call session_list
- "Carga la sesion 20260701-143052" → Call session_load with that name
- "Muestrame mas sesiones" → Call session_list with limit=10

Always confirm verbally when a session is restored:
- "He restaurado la sesion del 1 de julio con 24 mensajes"
- "No encontre esa sesion. Las disponibles son: ..."
