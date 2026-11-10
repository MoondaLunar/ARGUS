package com.crawler.controller;

import com.crawler.model.IntelligenceLink;
import com.crawler.model.DocumentArtifact;
import com.crawler.model.EntityGpsCluster;
import com.crawler.repository.IntelligenceLinkRepository;
import com.crawler.repository.DocumentArtifactRepository;
import com.crawler.repository.EntityGpsClusterRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
public class CrawlerController {

    @Autowired
    private IntelligenceLinkRepository linkRepository;

    @Autowired
    private DocumentArtifactRepository documentRepository;

    @Autowired
    private EntityGpsClusterRepository gpsClusterRepository;

    // Link endpoints
    @PostMapping("/links")
    public IntelligenceLink upsertLink(@RequestBody IntelligenceLink newLink) {
        return linkRepository.findByEntityAAndEntityB(newLink.getEntityA(), newLink.getEntityB())
            .map(existingLink -> {
                if (newLink.getConfidence() > existingLink.getConfidence()) {
                    existingLink.setConfidence(newLink.getConfidence());
                    existingLink.setRationale(newLink.getRationale());
                    existingLink.setSourceUrl(newLink.getSourceUrl());
                    existingLink.setLinkType(newLink.getLinkType());
                    existingLink.setMetadataEvidence(newLink.getMetadataEvidence());
                }
                return linkRepository.save(existingLink);
            })
            .orElseGet(() -> linkRepository.save(newLink));
    }

    @GetMapping("/links/entity/{entity}")
    public List<IntelligenceLink> getEntityConnections(@PathVariable String entity) {
        return linkRepository.findAllConnectionsForEntity(entity);
    }

    @GetMapping("/links/type/{linkType}")
    public List<IntelligenceLink> getLinksByType(@PathVariable String linkType) {
        return linkRepository.findByLinkType(linkType);
    }

    @GetMapping("/links/confidence/{minConfidence}")
    public List<IntelligenceLink> getHighConfidenceLinks(@PathVariable Double minConfidence) {
        return linkRepository.findHighConfidenceLinks(minConfidence);
    }

    @GetMapping("/links/gps/{geohash}")
    public List<IntelligenceLink> getLinksByGeohash(@PathVariable String geohash) {
        return linkRepository.findByGpsGeohash(geohash);
    }

    // Document endpoints
    @PostMapping("/documents")
    public DocumentArtifact saveDocument(@RequestBody DocumentArtifact document) {
        return documentRepository.save(document);
    }

    @GetMapping("/documents/hash/{hash}")
    public DocumentArtifact getDocumentByHash(@PathVariable String hash) {
        return documentRepository.findByHashMd5(hash).orElse(null);
    }

    @GetMapping("/documents/type/{docType}")
    public List<DocumentArtifact> getDocumentsByType(@PathVariable String docType) {
        return documentRepository.findByDocumentType(docType);
    }

    @GetMapping("/documents/images")
    public List<DocumentArtifact> getAllImages() {
        return documentRepository.findAllImages();
    }

    @GetMapping("/documents/pdfs")
    public List<DocumentArtifact> getAllPdfs() {
        return documentRepository.findAllPdfs();
    }

    @GetMapping("/documents/gps/{geohash}")
    public List<DocumentArtifact> getDocumentsByGeohash(@PathVariable String geohash) {
        return documentRepository.findByGpsGeohash(geohash);
    }

    @GetMapping("/documents/camera")
    public List<DocumentArtifact> getDocumentsByCamera(
            @RequestParam(required = false) String make,
            @RequestParam(required = false) String model) {
        return documentRepository.findByCamera(make, model);
    }

    // GPS Cluster endpoints
    @PostMapping("/clusters/gps")
    public EntityGpsCluster saveGpsCluster(@RequestBody EntityGpsCluster cluster) {
        return gpsClusterRepository.save(cluster);
    }

    @GetMapping("/clusters/gps/{geohash}")
    public List<EntityGpsCluster> getClustersByGeohash(@PathVariable String geohash) {
        return gpsClusterRepository.findByGeohash(geohash);
    }

    @GetMapping("/clusters/entity/{entity}")
    public List<EntityGpsCluster> getClustersByEntity(@PathVariable String entity) {
        return gpsClusterRepository.findByEntityName(entity);
    }

    @GetMapping("/clusters/confidence/{minConfidence}")
    public List<EntityGpsCluster> getHighConfidenceClusters(@PathVariable Double minConfidence) {
        return gpsClusterRepository.findHighConfidenceClusters(minConfidence);
    }

    @GetMapping("/clusters/corroborated/{minSightings}")
    public List<EntityGpsCluster> getCorroboratedClusters(@PathVariable Integer minSightings) {
        return gpsClusterRepository.findCorroboratedClusters(minSightings);
    }

    // Analytics endpoints
    @GetMapping("/analytics/summary")
    public Map<String, Object> getAnalyticsSummary() {
        return Map.of(
            "totalLinks", linkRepository.count(),
            "totalDocuments", documentRepository.count(),
            "totalGpsClusters", gpsClusterRepository.count(),
            "linksByType", Map.of(
                "entity_co-occurrence", linkRepository.findByLinkType("entity_co-occurrence").size(),
                "gps_proximity", linkRepository.findByLinkType("gps_proximity").size(),
                "metadata_match", linkRepository.findByLinkType("metadata_match").size()
            ),
            "documentsByType", Map.of(
                "images", documentRepository.findAllImages().size(),
                "pdfs", documentRepository.findAllPdfs().size()
            )
        );
    }

    @GetMapping("/analytics/top-entities")
    public List<Map<String, Object>> getTopEntities(@RequestParam(defaultValue = "10") int limit) {
        // This would require a more complex query; simplified here
        return List.of();
    }
}
