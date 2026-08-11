# Pattern di Architettura Master-Slave: Costruire Sistemi Distribuiti Scalabili

La replica del database è una delle sfide più antiche dei sistemi distribuiti, e l'architettura master-slave (ora spesso chiamata primary-replica) rimane una delle soluzioni più pratiche per scalare carichi di lavoro con molte letture. Ma non è una soluzione universale.

## Il Problema: Punto Unico di Collo di Bottiglia di Lettura

Immagina di aver costruito un microservizio che alimenta il motore di raccomandazioni della tua piattaforma. Ogni azione dell'utente—una ricerca, una visualizzazione, un clic—attiva letture dal database. Il tuo database può gestire bene le scritture, ma il traffico di lettura continua a crescere. Scala orizzontalmente aggiungendo server applicativi, ma colpiscono tutti lo stesso database. Il database diventa il tuo collo di bottiglia, e aggiungere più server non aiuta.

Entra il pattern master-slave: un database primario accetta scritture, e una o più repliche gestiscono letture. La tua applicazione scrive nel primario e legge dalle repliche, distribuendo il carico di lettura su più macchine.

## Come Funziona

```java
// Pseudo-codice che mostra la responsabilità divisa
public class DatabaseRouter {
    private Connection primary;      // Endpoint di scrittura
    private List<Connection> replicas; // Endpoint di lettura
    
    public void insertOrder(Order order) {
        // Tutte le scritture vanno al primario
        primary.executeUpdate("INSERT INTO orders ...");
    }
    
    public Order getOrder(String id) {
        // Le letture possono andare a qualsiasi replica
        Connection readDb = loadBalanceReplicas();
        return readDb.query("SELECT * FROM orders WHERE id = ?");
    }
}
```

Il primario replica i cambiamenti alle sue repliche usando un binary log (MySQL), write-ahead log (PostgreSQL), o un meccanismo equivalente. Le repliche applicano questi cambiamenti in modo asincrono, quindi sono eventualmente consistenti—non immediatamente consistenti. Questo è il compromesso.

## Quando Usarlo (E Quando No)

**Usa master-slave quando:**
- Il tuo carico di lavoro è pesante in letture (80%+ letture)
- Hai capacità di riserva sulle repliche durante le ore non di punta
- La consistenza eventuale è accettabile
- Stai usando un database che supporta nativamente la replicazione (MySQL, PostgreSQL, MongoDB)

**Non usarlo quando:**
- Le tue letture e scritture sono bilanciate (perché replicare?)
- Hai bisogno di forti garanzie di consistenza (applicazioni mission-critical come elaborazione pagamenti)
- Il lag di replicazione importa—i millisecondi contano negli scenari di trading ad alta frequenza
- Stai cercando di risolvere la scalabilità delle scritture (la replicazione aiuta solo le letture)

## Avvertenze del Mondo Reale

**Il lag di replicazione è reale.** Un utente crea un ordine nel primario, preme "Aggiorna", e legge da una replica che non si è ancora aggiornata. Vede "Ordine non trovato". Hai bisogno di logica di retry, strategie di invalidazione della cache, o instradamento delle scritture di nuovo al primario per un breve periodo.

**Il failover è complicato.** Se il tuo primario muore, promuovere una replica è una decisione gestionale, non automatica. Quale replica dovrebbe diventare primaria? È completamente aggiornata, o perderai dati? Ti sei perso una scrittura urgente? Framework popolari come Spring Data astraggono parte di questo, ma il problema rimane.

**Il monitoraggio è non negoziabile.** Metriche di lag di replica, controlli di salute primario/replica, e utilizzo del disco del write-ahead log hanno tutti bisogno di dashboard. Perdere un lag di replicazione che cresce lentamente fino a ore di ritardo è una modalità di guasto comune.

## Esempio con Spring Boot

```java
@Configuration
public class DataSourceConfig {
    
    @Bean
    public DataSource primaryDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://primary.db.example.com/mydb")
            .username("appuser").password("pass").build();
    }
    
    @Bean
    public DataSource replicaDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://replica.db.example.com/mydb")
            .username("appuser").password("pass").build();
    }
    
    @Bean
    public JdbcTemplate writeTemplate(DataSource primary) {
        return new JdbcTemplate(primary);
    }
    
    @Bean
    public JdbcTemplate readTemplate(DataSource replica) {
        return new JdbcTemplate(replica);
    }
}
```

Quindi inietta il template corretto in base all'operazione:

```java
@Service
public class OrderService {
    @Autowired private JdbcTemplate writeTemplate;
    @Autowired private JdbcTemplate readTemplate;
    
    public void saveOrder(Order o) {
        writeTemplate.update("INSERT INTO orders ...");
    }
    
    public Order findOrder(String id) {
        return readTemplate.query("SELECT * FROM orders WHERE id = ?");
    }
}
```

## Il Cambio Moderno: Repliche di Lettura su Master-Slave

I database nel cloud odierni (RDS, Cloud SQL, Azure Database) spesso usano la terminologia "read replicas" al posto di "slave"—in parte per sensibilità, in parte perché la divisione di responsabilità è più esplicita in un servizio gestito. Non gestisci tu stesso il protocollo di replicazione; lo fa il provider cloud. Semplicemente effettui il provisioning delle repliche e punti la tua applicazione ad esse.

## Takeaway Chiave

L'architettura master-slave è un elegante pattern per la scalabilità di lettura, ma è una soluzione tattica, non una panacea architettonica. Abbinala con monitoraggio solido, logica di retry, e garanzie di consistenza chiare nel tuo codice di applicazione. Quando il lag di replicazione o il failover diventano un punto di dolore frequente, potresti aver superato questo pattern—considera sharding, livelli di cache, o offerte database-as-a-service che gestiscono queste preoccupazioni per te.

Quali sfide di replicazione hai affrontato in produzione? Condividi la tua esperienza qui sotto.
