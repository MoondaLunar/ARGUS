package com.crawler.repository;

import com.crawler.model.DocumentArtifact;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface DocumentArtifactRepository extends JpaRepository<DocumentArtifact, Long> {
    
    Optional<DocumentArtifact> findByHashMd5(String hashMd5);
    Optional<DocumentArtifact> findByIdentifier(String identifier);
    
    List<DocumentArtifact> findBySourceType(String sourceType);
    List<DocumentArtifact> findByDocumentType(String documentType);
    
    @Query("SELECT d FROM DocumentArtifact d WHERE d.gpsGeohash = :geohash ORDER BY d.discoveredAt DESC")
    List<DocumentArtifact> findByGpsGeohash(@Param("geohash") String geohash);
    
    @Query("SELECT d FROM DocumentArtifact d WHERE d.cameraMake = :make OR d.cameraModel = :model")
    List<DocumentArtifact> findByCamera(@Param("make") String make, @Param("model") String model);
    
    @Query("SELECT COUNT(d) FROM DocumentArtifact d WHERE d.gpsGeohash = :geohash")
    long countByGpsGeohash(@Param("geohash") String geohash);
    
    @Query("SELECT d FROM DocumentArtifact d WHERE d.imageWidth IS NOT NULL AND d.imageHeight IS NOT NULL ORDER BY d.discoveredAt DESC")
    List<DocumentArtifact> findAllImages();
    
    @Query("SELECT d FROM DocumentArtifact d WHERE d.pdfPages IS NOT NULL ORDER BY d.discoveredAt DESC")
    List<DocumentArtifact> findAllPdfs();
}
