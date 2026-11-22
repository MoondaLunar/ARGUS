package com.intelligence.controller;

import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import com.intelligence.context.AuditContext;
import com.intelligence.service.CorroborationService;
import com.intelligence.service.EvidenceExportService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/intelligence")
public class IntelligenceController {

    private final IntelligenceFindingRepository repository;
    private final EvidenceExportService exportService;
    private final CorroborationService corroborationService;
    private final com.fasterxml.jackson.databind.ObjectMapper mapper;

    public IntelligenceController(IntelligenceFindingRepository repository, EvidenceExportService exportService, CorroborationService corroborationService, com.fasterxml.jackson.databind.ObjectMapper mapper) {
        this.mapper = mapper;
        this.repository = repository;
        this.exportService = exportService;
        this.corroborationService = corroborationService;
    }

    @PostMapping("/findings")
    public ResponseEntity<?> receiveFinding(
            @RequestBody IntelligenceFinding finding,
            @RequestHeader("X-Data-Hash") String dataHash,
            @RequestHeader("X-Build-Number") String buildNumber) {

        // Preserve client assertions separately before marking them unassessed.
        try { finding.setSubmittedAssessment(mapper.writeValueAsString(finding)); }
        catch (com.fasterxml.jackson.core.JsonProcessingException invalid) { return ResponseEntity.badRequest().build(); }
        finding.setSubmittedDataHash(dataHash);
        // The supplied hash is attribution metadata, not an integrity guarantee.
        finding.setId(null);
        finding.setDataHash(com.crawler.service.IngestionService.hash(
            java.util.Objects.toString(finding.getDescription(), "")));
        finding.setInfoCredibility("6");
        finding.setConfidenceLevel("Unassessed research observation");
        finding.setProbabilityPercentage(null);
        finding.setPersonaMatchScore(null);
        finding.setAuthenticityScore(null);

        // Set context for Hibernate Envers
        AuditContext.set(buildNumber, finding.getDataHash());
        try {
            // Apply military corroboration logic before saving
            corroborationService.processCorroboration(finding);
            return ResponseEntity.ok(repository.save(finding));
        } finally {
            AuditContext.clear();
        }
    }

    @GetMapping("/export/evidence")
    public ResponseEntity<byte[]> exportEvidence() {
        try {
            // Generates a PDF containing findings and Envers history, then PGP signs it
            byte[] signedPdf = exportService.generateSignedEvidencePdf();
            return ResponseEntity.ok()
                    .header("Content-Type", "application/zip")
                    .header("Content-Disposition", "attachment; filename=\"argus_evidence.zip\"")
                    .body(signedPdf);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}