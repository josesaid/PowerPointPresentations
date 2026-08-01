# Spring AI + Gemini: Integra i Modelli di Google nel tuo Spring Boot Senza Riscrivere Nulla

La maggior parte dei tutorial "aggiungi un LLM al tuo backend" finiscono con un mucchio di client HTTP fatti a mano, mapping JSON e logica di retry che marcisce nel momento in cui il provider cambia un campo. Spring AI fa una scommessa diversa: tratta un modello come Spring già tratta un datasource o un message broker — un bean che configuri con properties e inietti dove ne hai bisogno. Ecco come funziona con Gemini di Google, e le due trappole di configurazione che costano un pomeriggio intero alla gente.

## Un starter, due modi di autenticarsi

A partire dal 2026, il modulo che vuoi è lo starter Google GenAI. È quello che supporta **entrambi** l'API Gemini Developer gratuita (solo una chiave API) e il percorso pagato di Vertex AI (credenziali GCP) — lo stesso codice, configurazione diversa.

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-google-genai</artifactId>
</dependency>
```

Abbinalo con il BOM di Spring AI nel tuo `pom.xml` così non devi fissare la versione a mano. Per il **tier gratuito**, ottieni una chiave su aistudio.google.com/apikey (solo account Google, senza carta) e configura solo la chiave:

```yaml
spring:
  ai:
    google:
      genai:
        api-key: ${GEMINI_API_KEY}
        chat:
          model: gemini-2.5-flash
          temperature: 0.7
```

Per **Vertex AI** invece, abbandona la chiave API e fornisci un progetto e una posizione — Spring AI scopre automaticamente le tue credenziali `gcloud` application-default, quindi scrivi zero codice di autenticazione:

```yaml
spring:
  ai:
    google:
      genai:
        project-id: your-gcp-project
        location: us-central1
        chat:
          model: gemini-2.5-flash
```

## La vera chiamata è noiosa — che è il punto

Lo starter auto-configura un `ChatClient.Builder`. Iniettalo, costruisci una volta, e il codice di chiamata assomiglia identico a quello che scriveresti per OpenAI o Anthropic:

```java
@Service
public class GeminiService {

    private final ChatClient chatClient;

    public GeminiService(ChatClient.Builder builder) {
        this.chatClient = builder.build();
    }

    public String ask(String message) {
        return chatClient.prompt()
                .user(message)
                .call()
                .content();
    }
}
```

Cambiare provider più tardi significa cambiare la dipendenza e il blocco di configurazione — non questo servizio. Ecco l'intera proposta di valore: il modello diventa un dettaglio sostituibile, non una dipendenza rigida sparsa nel tuo codebase.

## Output strutturato invece di raschiare stringhe

La parte che risparmia il vero tempo in un backend è mappare la risposta del modello direttamente in un tipo Java, così non stai facendo regex su prosa:

```java
public record Summary(String headline, List<String> keyPoints) {}

public Summary summarize(String article) {
    return chatClient.prompt()
            .user(u -> u.text("Summarize this: {doc}").param("doc", article))
            .call()
            .entity(Summary.class);
}
```

Spring AI genera lo schema, chiede a Gemini di conformarsi, e deserializza la risposta nel tuo record. Da qui è un salto breve verso tool calling e RAG — lo stesso `ChatClient`, pochi metodi builder in più.

## Due trappole che sembrano bug ma non lo sono

**Deprecazione del modello.** `gemini-2.0-flash` è deprecato e viene spento — gli identificatori Gemini 1.x restituiscono già 404. Usa `gemini-2.5-flash`. Un errore di quota `limit: 0` di solito significa che il modello stesso ha perso capacità del tier gratuito, non che il tuo account sia throttled.

**Perdita della modalità auth.** Se imposti `project-id` o `location` *da qualsiasi parte* — anche rimasto da un esperimento — il client silenziosamente passa alla modalità Vertex AI e la tua chiave API Developer gratuita viene rifiutata con un 400 che sembra un problema di quota. Per il tier gratuito, imposta **solo** la chiave API ed elimina ogni traccia di project/location.

Entrambi hanno bruciato gente che assumeva che la sua chiave fosse cattiva quando la configurazione era il vero colpevole.

## Conclusione

L'astrazione di Spring AI guadagna la sua manutenzione il giorno in cui cambi Gemini con un altro modello e non tocchi nulla se non una dipendenza e un blocco YAML. Arrivarci costa uno starter, alcune properties, e ricordarsi che project-id è un cambio di modalità, non solo metadati.

Sei orientato verso l'API Developer gratuita per il prototipo, o vai direttamente a Vertex AI così prod e dev condividono un percorso di codice? Cosa ha inclinato la decisione per te?
