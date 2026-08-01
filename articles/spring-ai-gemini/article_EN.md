# Spring AI + Gemini: Add Google's Models to Your Spring Boot App Without Rewriting Anything

Most "add an LLM to your backend" tutorials end with a pile of hand-rolled HTTP clients, JSON mapping, and retry logic that rots the moment the provider changes a field. Spring AI takes a different bet: treat a model the same way Spring already treats a datasource or a message broker — a bean you configure with properties and inject where you need it. Here's how that plays out with Google's Gemini, and the two setup traps that cost people an afternoon.

## One starter, two ways to authenticate

As of 2026 the module you want is the Google GenAI starter. It's the one that supports **both** the free Gemini Developer API (just an API key) and the paid Vertex AI path (GCP credentials) — same code, different config.

```xml
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-starter-model-google-genai</artifactId>
</dependency>
```

Pair it with the Spring AI BOM in your `pom.xml` so you don't have to pin the version by hand. For the **free tier**, grab a key at aistudio.google.com/apikey (Google account only, no card) and configure just the key:

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

For **Vertex AI** instead, drop the API key and give it a project and location — Spring AI discovers your `gcloud` application-default credentials automatically, so you write zero auth code:

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

## The actual call is boring — which is the point

The starter auto-configures a `ChatClient.Builder`. Inject it, build once, and the calling code looks identical to what you'd write for OpenAI or Anthropic:

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

Swapping providers later means changing the dependency and the config block — not this service. That's the whole value proposition: the model becomes a replaceable detail, not a hard dependency threaded through your codebase.

## Structured output instead of string-scraping

The part that saves real time in a backend is mapping the model's answer straight onto a Java type, so you're not regex-ing prose:

```java
public record Summary(String headline, List<String> keyPoints) {}

public Summary summarize(String article) {
    return chatClient.prompt()
            .user(u -> u.text("Summarize this: {doc}").param("doc", article))
            .call()
            .entity(Summary.class);
}
```

Spring AI generates the schema, asks Gemini to conform, and deserializes the response into your record. From here it's a short hop to tool calling and RAG — same `ChatClient`, a few more builder methods.

## Two traps that look like bugs but aren't

**Model deprecation.** `gemini-2.0-flash` is deprecated and being shut down — Gemini 1.x identifiers already return 404. Use `gemini-2.5-flash`. A `limit: 0` quota error usually means the model itself lost free-tier capacity, not that your account is throttled.

**Auth-mode bleed.** If you set `project-id` or `location` *anywhere* — even left over from an experiment — the client silently switches to Vertex AI mode and your free Developer API key gets rejected with a 400 that reads like a quota problem. For the free tier, set **only** the API key and delete every trace of project/location.

Both of these have burned people who assumed their key was bad when the config was the real culprit.

## Wrap-up

The Spring AI abstraction earns its keep the day you swap Gemini for another model and touch nothing but a dependency and a YAML block. Getting there costs one starter, a few properties, and remembering that project-id is a mode switch, not just metadata.

Are you leaning toward the free Developer API for prototyping, or going straight to Vertex AI so prod and dev share one code path? What tipped the decision for you?
