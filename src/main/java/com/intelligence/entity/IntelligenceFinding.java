package com.intelligence.entity;

import lombok.Data;
import org.hibernate.envers.Audited;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "intelligence_findings")
@Data
@Audited
public class IntelligenceFinding {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String type;
    
    @Column(columnDefinition = "TEXT")
    private String description;
    
    private String sourceUrl;
    private String entity;
    private String discoveredBy; // The Agent name
    
    @Column(unique = false)
    private String dataHash; // SHA-256 of the core finding content

    private String sourceReliability; // A-F
    private String infoCredibility;   // 1-6
    private String confidenceLevel;   // ICD 203 Vocabulary (e.g., "Almost Certain")
    private String structuralFingerprint; // HTML Skeleton signature
    private Double personaMatchScore; // Likelihood of matching the Monica Witt behavioral archetype
    private Double authenticityScore; // Metric of organic vs performative rhetoric
    private Boolean deceptionFlag = false; // True if identified as a honeypot/clone
    
    private Integer probabilityPercentage; // 0-100 (Numerical mapping of ICD 203)
    private String analyticStandard = "ICD-203"; // Tracking the methodology used
    
    private LocalDateTime timestamp = LocalDateTime.now();
}