# Master-Slave Architecture Patterns: Building Scalable Distributed Systems

Database replication is one of the oldest distributed systems challenges, and master-slave (now often called primary-replica) architecture remains one of the most practical solutions for scaling read-heavy workloads. But it's not a silver bullet—understanding when and how to use it separates a working system from a fragile one.

## The Problem: Single Point of Read Bottleneck

Imagine you've built a microservice that powers your platform's recommendation engine. Every user action—a search, a view, a click—triggers database reads. Your database can handle writes fine, but read traffic keeps climbing. You scale horizontally by adding application servers, but they all hit the same database. The database becomes your bottleneck, and throwing more servers at the problem doesn't help.

Enter the master-slave pattern: one primary database accepts writes, and one or more replicas handle reads. Your application writes to the primary and reads from replicas, distributing read load across multiple machines.

## How It Works

```java
// Pseudo-code showing the split responsibility
public class DatabaseRouter {
    private Connection primary;      // Write endpoint
    private List<Connection> replicas; // Read endpoints
    
    public void insertOrder(Order order) {
        // All writes go to primary
        primary.executeUpdate("INSERT INTO orders ...");
    }
    
    public Order getOrder(String id) {
        // Reads can go to any replica
        Connection readDb = loadBalanceReplicas();
        return readDb.query("SELECT * FROM orders WHERE id = ?");
    }
}
```

The primary replicates changes to its replicas using a binary log (MySQL), write-ahead log (PostgreSQL), or an equivalent mechanism. Replicas apply these changes asynchronously, so they're eventually consistent—not immediately consistent. That's the trade-off.

## When to Use It (And When Not To)

**Use master-slave when:**
- Your workload is read-heavy (80%+ reads)
- You have spare capacity on replicas during off-peak hours
- Eventual consistency is acceptable
- You're using a database that supports replication natively (MySQL, PostgreSQL, MongoDB)

**Don't use it when:**
- Your reads and writes are balanced (why replicate?)
- You need strong consistency guarantees (strict-consistency applications like payment processing)
- Replication lag matters—milliseconds count in high-frequency trading scenarios
- You're trying to solve write scalability (replication only helps reads)

## Real-World Caveats

**Replication lag is real.** A user creates an order on the primary, hits "Refresh," and reads from a replica that hasn't caught up yet. They see "Order not found." You need retry logic, cache invalidation strategies, or routing writes back to the primary for a brief window.

**Failover is messy.** If your primary dies, promoting a replica is a management decision, not automatic. Which replica should become primary? Is it fully caught up, or will you lose data? Did you miss an urgent write? Popular frameworks like Spring Data abstract some of this, but the problem remains.

**Monitoring is non-negotiable.** Replication lag metrics, primary/replica health checks, and write-ahead log disk usage all need dashboards. Missing a creeping replication lag until it's hours behind is a common failure mode.

## Spring Boot Example

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

Then inject the right template based on the operation:

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

## The Modern Shift: Read Replicas Over Master-Slave

Today's cloud databases (RDS, Cloud SQL, Azure Database) often use "read replicas" terminology instead of "slave"—partly for sensitivity, partly because the responsibility split is more explicit in a managed service. You don't manage the replication protocol yourself; the cloud provider does. You just provision replicas and point your application at them.

## Key Takeaway

Master-slave architecture is an elegant pattern for read scaling, but it's a tactical solution, not a architectural panacea. Pair it with solid monitoring, retry logic, and clear consistency guarantees in your application code. When replication lag or failover becomes a frequent pain point, you might be outgrowing this pattern—consider sharding, caching layers, or database-as-a-service offerings that handle these concerns for you.

What replication challenges have you hit in production? Share your experience below.
