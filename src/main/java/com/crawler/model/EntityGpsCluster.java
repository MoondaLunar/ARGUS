package com.crawler.model;

import org.hibernate.envers.Audited;
import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "entity_gps_clusters", indexes = {
    @Index(name = "idx_geohash", columnList = "geohash"),
    @Index(name = "idx_entity", columnList = "entityName"),
    @Index(name = "idx_clusters_confidence", columnList = "confidence"),
})
@Data
@Audited
public class EntityGpsCluster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String entityName;

    @Column(nullable = false)
    private Double latitude;

    @Column(nullable = false)
    private Double longitude;

    @Column(nullable = false)
    private String geohash; // Precision hash for proximity

    @Column(nullable = false)
    private Integer sightings; // Number of evidence pieces

    @Column(nullable = false)
    private Double confidence; // Based on corroboration

    @Column(columnDefinition = "LONGTEXT")
    private String evidence; // JSON array of document references

    @Column(name = "first_seen")
    private java.time.LocalDateTime firstSeen;

    @Column(name = "last_seen")
    private java.time.LocalDateTime lastSeen;

    public EntityGpsCluster() {}

    public EntityGpsCluster(String entityName, Double latitude, Double longitude, String geohash) {
        this.entityName = entityName;
        this.latitude = latitude;
        this.longitude = longitude;
        this.geohash = geohash;
        this.sightings = 1;
        this.confidence = 0.0;
        this.firstSeen = java.time.LocalDateTime.now();
        this.lastSeen = java.time.LocalDateTime.now();
    }
}
