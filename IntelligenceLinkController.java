package com.crawler.controller;

import com.crawler.model.IntelligenceLink;
import com.crawler.repository.IntelligenceLinkRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/links")
public class IntelligenceLinkController {

    @Autowired
    private IntelligenceLinkRepository repository;

    @PostMapping
    public IntelligenceLink upsertLink(@RequestBody IntelligenceLink newLink) {
        return repository.findByEntityAAndEntityB(newLink.getEntityA(), newLink.getEntityB())
            .map(existingLink -> {
                // Only update if the new confidence is higher or from a new source
                if (newLink.getConfidence() > existingLink.getConfidence()) {
                    existingLink.setConfidence(newLink.getConfidence());
                    existingLink.setRationale(newLink.getRationale());
                    existingLink.setSourceUrl(newLink.getSourceUrl());
                }
                return repository.save(existingLink);
            })
            .orElseGet(() -> repository.save(newLink));
    }
}