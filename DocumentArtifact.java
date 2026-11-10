package com.crawler.model;

import org.hibernate.envers.Audited;
import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "document_artifacts", indexes = {
    @Index(name = "idx_source_type", columnList = "sourceType"),
    @Index(name = "idx_hash", columnList = "hashMd5"),
    @Index(name = "idx_gps", columnList = "gpsGeohash"),
})
@Data
@Audited
public class DocumentArtifact {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String sourceType; // web, local, archive

    @Column(nullable = false, unique = true)
    private String identifier; // URL or file path

    private String documentType; // image, pdf, html, archive, etc

    @Column(columnDefinition = "TEXT")
    private String url;

    @Column(columnDefinition = "TEXT")
    private String filePath;

    @Column(columnDefinition = "LONGTEXT")
    private String metadata; // JSON: EXIF, PDF props, etc

    @Column(columnDefinition = "LONGTEXT")
    private String extractedText; // Preview of content

    private String hashMd5;
    private Long fileSize;

    // GPS info
    private Double gpsLatitude;
    private Double gpsLongitude;
    private String gpsGeohash;
    private java.time.LocalDateTime gpsCaptureTime;

    // Image specific
    private Integer imageWidth;
    private Integer imageHeight;
    private String cameraMake;
    private String cameraModel;

    // PDF specific
    private Integer pdfPages;
    private String pdfTitle;
    private String pdfAuthor;

    @Column(name = "discovered_at", nullable = false, updatable = false)
    private java.time.LocalDateTime discoveredAt = java.time.LocalDateTime.now();

    @Column(name = "indexed_at")
    private java.time.LocalDateTime indexedAt;

    public DocumentArtifact() {}

    public DocumentArtifact(String sourceType, String identifier, String documentType) {
        this.sourceType = sourceType;
        this.identifier = identifier;
        this.documentType = documentType;
    }
}
