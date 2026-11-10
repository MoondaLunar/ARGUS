package com.crawler.repository;

import com.crawler.model.EntityGpsCluster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface EntityGpsClusterRepository extends JpaRepository<EntityGpsCluster, Long> {
    
    Optional<EntityGpsCluster> findByEntityNameAndGeohash(String entityName, String geohash);
    
    List<EntityGpsCluster> findByEntityName(String entityName);
    
    @Query("SELECT c FROM EntityGpsCluster c WHERE c.geohash = :geohash ORDER BY c.sightings DESC")
    List<EntityGpsCluster> findByGeohash(@Param("geohash") String geohash);
    
    @Query("SELECT c FROM EntityGpsCluster c WHERE c.confidence >= :minConfidence ORDER BY c.confidence DESC, c.sightings DESC")
    List<EntityGpsCluster> findHighConfidenceClusters(@Param("minConfidence") Double minConfidence);
    
    @Query("SELECT c FROM EntityGpsCluster c WHERE c.sightings >= :minSightings ORDER BY c.sightings DESC")
    List<EntityGpsCluster> findCorroboratedClusters(@Param("minSightings") Integer minSightings);
}
