package com.crawler.repository;

import com.crawler.model.IntelligenceLink;
import com.crawler.model.DocumentArtifact;
import com.crawler.model.EntityGpsCluster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface IntelligenceLinkRepository extends JpaRepository<IntelligenceLink, Long> {
    
    Optional<IntelligenceLink> findByEntityAAndEntityB(String entityA, String entityB);
    
    List<IntelligenceLink> findByEntityA(String entityA);
    List<IntelligenceLink> findByEntityB(String entityB);
    
    @Query("SELECT l FROM IntelligenceLink l WHERE (l.entityA = :entity OR l.entityB = :entity) ORDER BY l.confidence DESC")
    List<IntelligenceLink> findAllConnectionsForEntity(@Param("entity") String entity);
    
    @Query("SELECT l FROM IntelligenceLink l WHERE l.confidence >= :minConfidence ORDER BY l.confidence DESC")
    List<IntelligenceLink> findHighConfidenceLinks(@Param("minConfidence") Double minConfidence);
    
    @Query("SELECT l FROM IntelligenceLink l WHERE l.linkType = :linkType ORDER BY l.createdAt DESC")
    List<IntelligenceLink> findByLinkType(@Param("linkType") String linkType);
    
    @Query("SELECT COUNT(l) FROM IntelligenceLink l WHERE l.gpsGeohash IS NOT NULL AND l.gpsGeohash = :geohash")
    long countByGpsGeohash(@Param("geohash") String geohash);

    @Query("SELECT l FROM IntelligenceLink l WHERE l.gpsGeohash = :geohash ORDER BY l.confidence DESC")
    List<IntelligenceLink> findByGpsGeohash(@Param("geohash") String geohash);
}
