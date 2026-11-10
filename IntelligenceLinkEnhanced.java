package com.crawler.model;

import org.hibernate.envers.Audited;
import jakarta.persistence.*;
import lombok.Data;
import com.fasterxml.jackson.databind.JsonNode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "intelligence_links", indexes = {
    @Index(name = "idx_entities", columnList = "entityA,entityB"),
    @Index(name = "idx_link_type", columnList = "linkType"),
    @Index(name = "idx_confidence", columnList = "confidence"),
})
@Data
@Audited
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

    @Column(name = "linkType", nullable = false)
    private String linkType = "entity_co-occurrence"; // entity_co-occurrence, gps_proximity, metadata_match, document_co-occurrence

    @Column(columnDefinition = "LONGTEXT")
    private String metadataEvidence; // JSON serialized metadata

    @Column(name = "created_at", nullable = false, updatable = false)
    private java.time.LocalDateTime createdAt = java.time.LocalDateTime.now();

    @Column(name = "updated_at")
    private java.time.LocalDateTime updatedAt = java.time.LocalDateTime.now();

    // GPS proximity info
    private Double gpsLatitude;
    private Double gpsLongitude;
    private String gpsGeohash;

    public IntelligenceLink() {}

    public IntelligenceLink(String entityA, String entityB, Double confidence, String rationale, String sourceUrl) {
        this.entityA = entityA;
        this.entityB = entityB;
        this.confidence = confidence;
        this.rationale = rationale;
        this.sourceUrl = sourceUrl;
    }
}
