# 📢 PUBLICAR A DEV.TO

El artículo está completamente listo. Usa **uno de estos métodos** para publicar:

## Opción 1: Ejecutar localmente (Recomendado - Más rápido)

```bash
cd articles/spring-ai-gemini

# Asegúrate de tener Node.js instalado
export DEVTO_API_KEY="6RANyTeipK9AgyWN7Q2T1PLH"

# Publicar artículo EN
node publish-to-devto.js article_EN.md

# Esto guardará la URL en devto-published-state.json
cat devto-published-state.json
```

**Resultado esperado:**
```
✅ Published successfully!
📎 URL: https://dev.to/said_olano/spring-ai-gemini-...
```

## Opción 2: Usar GitHub CLI (desde tu máquina)

```bash
# Trigger workflow dispatch si existe
gh workflow run publish-spring-ai-gemini.yml --ref master

# O simplemente clone y ejecute
git clone https://github.com/josesaid/PowerPointPresentations.git
cd PowerPointPresentations/articles/spring-ai-gemini
export DEVTO_API_KEY="6RANyTeipK9AgyWN7Q2T1PLH"
node publish-to-devto.js article_EN.md
```

## Opción 3: GitHub Actions (Configuración Manual)

Si tienes acceso a Settings > Secrets en el repo:

1. Añade secret: `DEVTO_API_KEY` = `6RANyTeipK9AgyWN7Q2T1PLH`
2. Crea workflow `.github/workflows/publish-devto.yml`:

```yaml
name: Publish Spring AI Article

on:
  workflow_dispatch:

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - name: Publish to dev.to
        env:
          DEVTO_API_KEY: ${{ secrets.DEVTO_API_KEY }}
        run: |
          cd articles/spring-ai-gemini
          node publish-to-devto.js article_EN.md
```

3. Go to Actions > Workflows > Manually trigger

## Qué pasará

El script `publish-to-devto.js`:

1. ✅ Lee `article_EN.md`
2. ✅ Extrae título (primera línea con `# `)
3. ✅ Envía a dev.to API con tags: `springai`, `java`, `gemini`, `ai`
4. ✅ Guarda estado en `devto-published-state.json` con:
   - URL publicada
   - Slug
   - ID del artículo
   - Timestamp

## Después de publicar

1. Verifica que existe en dev.to: https://dev.to/said_olano
2. Copia la URL real (reemplazará el placeholder en LinkedIn)
3. Actualiza `temas_post_LinkedIn_usados.txt` con:
   ```
   Spring AI + Gemini: Google's Models in Spring Boot
     └─ Publicado: 2026-08-01
     └─ Plataformas: dev.to ✅ | LinkedIn ⏳ | GitHub ✅
   ```

## Contenido disponible

✅ **article_EN.md** - Artículo en inglés (700+ palabras)
✅ **SpringAI_Gemini_ES.md** - Artículo en español
✅ **SpringAI_Gemini_IT.md** - Artículo en italiano
✅ **SpringAI_Gemini_EN.pdf** - PDF con portada (inglés)
✅ **SpringAI_Gemini_ES.pdf** - PDF con portada (español)
✅ **SpringAI_Gemini_IT.pdf** - PDF con portada (italiano)
✅ **cover.png** - Portada 1200×630
✅ **publish-to-devto.js** - Script de publicación

## Troubleshooting

**Error: `API key error`**
- Verifica que `DEVTO_API_KEY` esté configurada
- Verifica que la API key sea correcta: `6RANyTeipK9AgyWN7Q2T1PLH`

**Error: `Article already exists`**
- El artículo ya fue publicado
- Busca en https://dev.to/said_olano
- Verifica `devto-published-state.json` para la URL

**Error: `Host not in allowlist`**
- El servidor/contenedor no tiene acceso a dev.to
- Ejecuta desde tu máquina local O desde GitHub Actions

---

**Ready to publish. Choose one method above and run.**
