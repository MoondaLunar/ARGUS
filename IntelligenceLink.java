import org.hibernate.envers.Audited;
import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "intelligence_links")
@Data
@Audited // This annotation triggers Hibernate Envers to create _AUD tables for versioning
public class IntelligenceLink {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String entityA;
    private String entityB;
    
    private Double confidence;
    
    @Column(columnDefinition = "TEXT")
    private String rationale;

    private String sourceUrl;

    // Hibernate Envers will automatically track changes to 'confidence' and 'rationale'
    // allowing you to see how the LLM's "opinion" of a link changed over multiple crawls.
}