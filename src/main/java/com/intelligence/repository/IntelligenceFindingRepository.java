package com.intelligence.repository;

import com.intelligence.entity.IntelligenceFinding;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface IntelligenceFindingRepository extends JpaRepository<IntelligenceFinding, Long> {
    List<IntelligenceFinding> findByDataHash(String dataHash);
}