# GitHub Repository Management

## 🚀 Automatisches Repository Setup

Jedes Projekt bekommt automatisch ein GitHub Repository mit dem Format:
```
https://github.com/svnstfns/cccli_<PROJECT_NUMBER>-<PROJECT_NAME>
```

## 📝 Commands in Claude Code CLI

### Repository erstellen/verbinden
```bash
# In Claude Code CLI:
/github init

# Oder manuell:
cd 002-gopro-streaming
./github-manager.sh init
```

### Increments committen
```bash
# Nach jedem Arbeitsschritt in Claude:
/github commit "feat: added streaming config"

# Oder automatisch nach /implement:
/implement feature XY    # committed automatisch am Ende
```

### Workflow Beispiel

#### 1. Neues Projekt starten
```bash
cd /Users/sst/gh-projects/cccli/003-new-project
claude

# In Claude:
/github init               # Repo wird angelegt: cccli_003-new-project
/architecture             # Plane Architektur
/github commit "docs: initial architecture"
```

#### 2. Feature entwickeln
```bash
/implement user authentication
# ... Claude entwickelt Feature ...
# Am Ende automatisch: git commit -m "feat: user authentication"

/test
# ... Tests werden geschrieben ...
# Automatisch: git commit -m "test: added auth tests"
```

#### 3. Bug fixen
```bash
/debug login-issue
# ... Claude analysiert und fixt ...
# Automatisch: git commit -m "fix: resolved login issue"
```

## 🔄 Automatisierung

### In CLAUDE.md eines Projekts hinzufügen:
```markdown
## Git Integration
- Auto-commit nach jedem /implement, /test, /fix Command
- Branch-Strategie: main + feature branches  
- Naming: cccli_002-gopro-streaming

## Commands
/github init     # Repository Setup
/github commit   # Manueller Commit
/github pr       # Pull Request erstellen
```

### In project-state.json wird getrackt:
```json
{
  "github": {
    "repository": "cccli_002-gopro-streaming",
    "current_branch": "main",
    "last_commit": "abc123",
    "increments_count": 42
  }
}
```

## 🛠️ Setup Checkliste

- [ ] GitHub CLI installiert (`brew install gh`)
- [ ] GitHub CLI authentifiziert (`gh auth login`)
- [ ] `.mcp.json` mit GitHub MCP Server konfiguriert
- [ ] `github-manager.sh` executable (`chmod +x github-manager.sh`)

## 📊 Repository Struktur

```
github.com/svnstfns/
├── cccli_001-rss-to-plex/
├── cccli_002-gopro-streaming/
└── cccli_003-next-project/
```

Jedes Repo enthält:
- Den kompletten Source Code aus `source/`
- Die Claude-Konfiguration aus `.claude-project/`
- Automatische Commit-Historie der Increments
- README mit Projekt-Beschreibung

## 🎯 Best Practices

1. **Kleine Increments**: Jeder Schritt = ein Commit
2. **Klare Messages**: `feat:`, `fix:`, `docs:`, `test:`
3. **Feature Branches**: Bei größeren Änderungen
4. **Pull Requests**: Für Code Review

## 💡 Tipps

- Nutze `/github status` um den aktuellen Stand zu sehen
- Commits werden auch in SQLite gespeichert für Memory
- Bei Problemen: `gh repo view svnstfns/cccli_002-gopro-streaming`
