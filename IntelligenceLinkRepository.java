package com.crawler.repository;

import com.crawler.model.IntelligenceLink;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface IntelligenceLinkRepository extends JpaRepository<IntelligenceLink, Long> {
    Optional<IntelligenceLink> findByEntityAAndEntityB(String entityA, String entityB);
}