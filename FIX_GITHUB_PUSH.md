# 🔒 Fix GitHub Push - Secret Détecté

## ❌ Erreur GitHub

```
remote: - Push cannot contain secrets
remote:   —— Groq API Key ——————————————————————————————————————
remote:     locations:
remote:       - commit: 570fe8e4aa8b016f516b683d296957983f390c36
remote:         path: RESTART_BACKEND.bat:19
```

GitHub a détecté une **clé API Groq** dans votre code et bloque le push pour des raisons de sécurité.

---

## ✅ Solution (3 Étapes)

### Étape 1 : Supprimer la Clé du Commit

```bash
# Annuler le dernier commit (garde les modifications)
git reset --soft HEAD~1

# Ou annuler et supprimer les modifications
git reset --hard HEAD~1
```

---

### Étape 2 : Nettoyer les Fichiers avec des Clés

Les fichiers suivants contiennent des clés API et ne doivent **PAS** être commités :

```
backend/.env
graph agent/.env
RESTART_BACKEND.bat (déjà corrigé)
```

Vérifiez qu'ils sont dans `.gitignore` :

```bash
# Créer/modifier .gitignore
notepad .gitignore
```

Ajoutez ces lignes :
```
# Environment variables (contiennent des clés API)
.env
*.env
backend/.env
graph agent/.env

# Node modules
node_modules/
*/node_modules/

# Python
__pycache__/
*.pyc
venv/
*/venv/

# Build
dist/
build/
*.log
```

---

### Étape 3 : Recommiter Sans les Clés

```bash
# Ajouter tous les fichiers SAUF ceux dans .gitignore
git add .

# Vérifier ce qui sera commité
git status

# Commiter
git commit -m "Initial commit - BlockStat Pro"

# Pusher
git push -u origin main
```

---

## 🔍 Vérification Avant Push

### Vérifier qu'aucune clé n'est dans le commit

```bash
# Voir les fichiers qui seront commités
git status

# Voir le contenu des fichiers modifiés
git diff --cached
```

**Assurez-vous que vous ne voyez PAS** :
- ❌ `GROQ_API_KEY=gsk_...`
- ❌ `ALCHEMY_API_KEY=...`
- ❌ `BITQUERY_ACCESS_TOKEN=...`
- ❌ Fichiers `.env`

---

## 🛡️ Bonnes Pratiques

### 1. Toujours Utiliser .gitignore

```
.env
*.env
```

### 2. Utiliser des Fichiers .env.example

Créez des fichiers d'exemple SANS les vraies clés :

**backend/.env.example** :
```
PORT=5000
NODE_ENV=development
GRAPH_AGENT_URL=http://localhost:8000
GROQ_API_KEY=your_groq_api_key_here
```

**graph agent/.env.example** :
```
ALCHEMY_API_KEY=your_alchemy_key_here
BITQUERY_ACCESS_TOKEN=your_bitquery_token_here
ETHERSCAN_API_KEY=your_etherscan_key_here
```

Ces fichiers `.env.example` peuvent être commités car ils ne contiennent pas de vraies clés.

---

### 3. Documentation dans README

Ajoutez dans votre README :

```markdown
## Configuration

1. Copier les fichiers d'exemple :
   ```bash
   cp backend/.env.example backend/.env
   cp "graph agent/.env.example" "graph agent/.env"
   ```

2. Modifier les fichiers `.env` avec vos vraies clés API :
   - GROQ_API_KEY : https://console.groq.com/keys
   - ALCHEMY_API_KEY : https://dashboard.alchemy.com/
   - BITQUERY_ACCESS_TOKEN : https://graphql.bitquery.io/
```

---

## 🔧 Commandes Complètes

### Solution Rapide (Copier-Coller)

```bash
# 1. Annuler le commit avec la clé
git reset --soft HEAD~1

# 2. Créer .gitignore
echo .env >> .gitignore
echo *.env >> .gitignore
echo backend/.env >> .gitignore
echo "graph agent/.env" >> .gitignore
echo node_modules/ >> .gitignore
echo __pycache__/ >> .gitignore
echo venv/ >> .gitignore
echo dist/ >> .gitignore

# 3. Ajouter .gitignore au commit
git add .gitignore

# 4. Ajouter les autres fichiers (sauf .env)
git add .

# 5. Vérifier qu'aucun .env n'est ajouté
git status

# 6. Commiter
git commit -m "Initial commit - BlockStat Pro"

# 7. Pusher
git push -u origin main
```

---

## 🚨 Si la Clé est Déjà sur GitHub

Si vous avez déjà pushé une clé API sur GitHub :

### 1. Révoquer la Clé Immédiatement

- **Groq** : https://console.groq.com/keys → Supprimer la clé
- **Alchemy** : https://dashboard.alchemy.com/ → Supprimer la clé
- **BitQuery** : https://graphql.bitquery.io/ → Révoquer le token

### 2. Générer de Nouvelles Clés

Créez de nouvelles clés API et mettez-les dans vos fichiers `.env` locaux.

### 3. Nettoyer l'Historique Git

```bash
# Supprimer le fichier de l'historique
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

**⚠️ Attention** : `git filter-branch` réécrit l'historique. À utiliser avec précaution.

---

## 📋 Checklist

- [ ] Annulé le commit avec `git reset --soft HEAD~1`
- [ ] Créé/mis à jour `.gitignore`
- [ ] Vérifié que `.env` est dans `.gitignore`
- [ ] Vérifié avec `git status` qu'aucun `.env` n'est ajouté
- [ ] Recommité sans les clés
- [ ] Pushé avec succès
- [ ] Révoqué les anciennes clés (si déjà pushées)
- [ ] Généré de nouvelles clés

---

## 🎯 Résumé

### Problème
```
GitHub détecte une clé API dans le code
    ↓
Bloque le push pour sécurité
```

### Solution
```
1. Annuler le commit
2. Ajouter .env dans .gitignore
3. Recommiter sans les clés
4. Pusher
```

---

## 🔗 Liens Utiles

- **GitHub Secret Scanning** : https://docs.github.com/code-security/secret-scanning
- **Groq Console** : https://console.groq.com/keys
- **Alchemy Dashboard** : https://dashboard.alchemy.com/
- **Git Filter Branch** : https://git-scm.com/docs/git-filter-branch

---

**Bon fix !** 🔒
