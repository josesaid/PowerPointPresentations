# Spring AI + Gemini: Integra los Modelos de Google en tu Spring Boot sin Reescribir Nada

La mayoría de tutoriales "añade un LLM a tu backend" terminan con un montón de clientes HTTP hechos a mano, mapeos JSON y lógica de reintentos que se pudre en el momento que el proveedor cambia un campo. Spring AI apuesta por otro camino: trata un modelo como Spring ya trata una fuente de datos o un message broker — un bean que configuras con properties e inyectas donde lo necesites. Aquí es cómo funciona eso con Gemini de Google, y las dos trampas de configuración que le cuestan una tarde a la gente.

## Un starter, dos formas de autenticarse

A partir de 2026, el módulo que quieres es el Google GenAI starter. Es el que soporta **ambos** la API de Gemini Developer gratuita (solo una API key) y la ruta pagada de Vertex AI (credenciales de GCP) — el mismo código, diferente config.

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-google-genai</artifactId>
</dependency>
```

Emparéjalo con el Spring AI BOM en tu `pom.xml` para que no tengas que fijar la versión manualmente. Para el **tier gratuito**, obtén una clave en aistudio.google.com/apikey (solo cuenta de Google, sin tarjeta) y configura solo la clave:

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

Para **Vertex AI** en su lugar, suelta la API key y dale un proyecto y ubicación — Spring AI descubre tus credenciales `gcloud` application-default automáticamente, así que escribes cero código de autenticación:

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

## La llamada real es aburrida — que es el punto

El starter auto-configura un `ChatClient.Builder`. Inyéctalo, construye una vez, y el código de llamada se ve idéntico a lo que escribirías para OpenAI o Anthropic:

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

Cambiar proveedores más tarde significa cambiar la dependencia y el bloque de config — no este servicio. Esa es toda la propuesta de valor: el modelo se convierte en un detalle reemplazable, no en una dependencia dura atravesada por tu codebase.

## Salida estructurada en lugar de raspar strings

La parte que ahorra tiempo real en un backend es mapear la respuesta del modelo directamente en un tipo Java, para que no estés haciendo regex en prosa:

```java
public record Summary(String headline, List<String> keyPoints) {}

public Summary summarize(String article) {
    return chatClient.prompt()
            .user(u -> u.text("Summarize this: {doc}").param("doc", article))
            .call()
            .entity(Summary.class);
}
```

Spring AI genera el schema, le pide a Gemini que se conforme, y deserializa la respuesta en tu record. Desde aquí es un salto corto a tool calling y RAG — el mismo `ChatClient`, algunos métodos builder más.

## Dos trampas que parecen bugs pero no lo son

**Deprecación de modelo.** `gemini-2.0-flash` está deprecado y siendo apagado — los identificadores Gemini 1.x ya devuelven 404. Usa `gemini-2.5-flash`. Un error de cuota `limit: 0` generalmente significa que el modelo mismo perdió capacidad del tier gratuito, no que tu cuenta esté throttled.

**Sangrado de modo de auth.** Si estableces `project-id` o `location` *en cualquier lugar* — incluso dejado de un experimento — el cliente silenciosamente se cambia a modo Vertex AI y tu clave API de Developer gratuita se rechaza con un 400 que se ve como un problema de cuota. Para el tier gratuito, establece **solo** la API key y elimina todo rastro de project/location.

Ambas han quemado a gente que asumía que su clave era mala cuando la config era el culpable real.

## Conclusión

La abstracción de Spring AI se gana su mantención el día que cambias Gemini por otro modelo y tocas nada más que una dependencia y un bloque YAML. Llegar ahí cuesta un starter, algunas properties, y recordar que project-id es un cambio de modo, no solo metadata.

¿Te inclinas hacia la API de Developer gratuita para prototipado, o vas directo a Vertex AI para que prod y dev compartan un camino de código? ¿Qué inclinó la decisión para ti?
