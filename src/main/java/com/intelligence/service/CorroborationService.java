package com.intelligence.service;

import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import org.springframework.stereotype.Service;

/** Identical content is a duplicate candidate, never independent corroboration. */
@Service
public class CorroborationService {
    private final IntelligenceFindingRepository repository;
    public CorroborationService(IntelligenceFindingRepository repository) { this.repository = repository; }

    public void processCorroboration(IntelligenceFinding incoming) {
        if (incoming.getDataHash() == null || incoming.getDataHash().isBlank()) return;
        if (!repository.findByDataHash(incoming.getDataHash()).isEmpty()) {
            incoming.setDescription(java.util.Objects.toString(incoming.getDescription(), "") +
                " [Matching stored content exists; source independence and truth have not been verified.]");
        }
    }
}