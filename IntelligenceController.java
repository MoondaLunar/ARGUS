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

    public IntelligenceController(IntelligenceFindingRepository repository, EvidenceExportService exportService, CorroborationService corroborationService) {
        this.repository = repository;
        this.exportService = exportService;
        this.corroborationService = corroborationService;
    }

    @PostMapping("/findings")
    public ResponseEntity<?> receiveFinding(
            @RequestBody IntelligenceFinding finding,
            @RequestHeader("X-Data-Hash") String dataHash,
            @RequestHeader("X-Build-Number") String buildNumber) {

        finding.setDataHash(dataHash);

        // Set context for Hibernate Envers
        AuditContext.set(buildNumber, dataHash);
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
                    .header("Content-Type", "application/pdf")
                    .header("Content-Disposition", "attachment; filename=\"sentinel_evidence_signed.pdf\"")
                    .body(signedPdf);
        } catch (Exception e) {
            return ResponseEntity.internalServerError().build();
        }
    }
}