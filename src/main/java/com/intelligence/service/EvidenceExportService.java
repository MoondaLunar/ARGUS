package com.intelligence.service;

import com.intelligence.audit.AuditRevisionEntity;
import com.intelligence.entity.IntelligenceFinding;
import com.intelligence.repository.IntelligenceFindingRepository;
import com.lowagie.text.*;
import com.lowagie.text.pdf.PdfWriter;
import org.hibernate.envers.AuditReader;
import org.hibernate.envers.AuditReaderFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import java.io.ByteArrayOutputStream;
import java.util.List;

@Service
public class EvidenceExportService {

    @PersistenceContext
    private EntityManager entityManager;

    @Autowired
    private IntelligenceFindingRepository repository;

    @Autowired
    private PgpSigningService pgpSigningService;

    @org.springframework.transaction.annotation.Transactional(readOnly = true)
    public byte[] generateSignedEvidencePdf() throws Exception {
        byte[] pdfBytes = generatePdfReport();
        byte[] signature = pgpSigningService.signData(pdfBytes);
        ByteArrayOutputStream output = new ByteArrayOutputStream();
        try (var zip = new java.util.zip.ZipOutputStream(output)) {
            zip.putNextEntry(new java.util.zip.ZipEntry("evidence.pdf"));
            zip.write(pdfBytes); zip.closeEntry();
            zip.putNextEntry(new java.util.zip.ZipEntry("evidence.pdf.sig"));
            zip.write(signature); zip.closeEntry();
        }
        return output.toByteArray();
    }

    private byte[] generatePdfReport() throws Exception {
        List<IntelligenceFinding> findings = repository.findAll();
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        Document document = new Document(PageSize.A4);
        PdfWriter.getInstance(document, out);
        document.open();

        Font titleFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 18);
        Font sectionFont = FontFactory.getFont(FontFactory.HELVETICA_BOLD, 12);
        Font normalFont = FontFactory.getFont(FontFactory.HELVETICA, 10);
        Font auditFont = FontFactory.getFont(FontFactory.COURIER, 8);

        document.add(new Paragraph("ARGUS RESEARCH OBSERVATIONS - NOT AN OFFICIAL FINDING", titleFont));
        document.add(new Paragraph("Candidate evidence; identity and source independence require review", normalFont));
        document.add(new Paragraph("Export Timestamp: " + java.time.LocalDateTime.now(), normalFont));
        document.add(new Paragraph("\n"));

        AuditReader auditReader = AuditReaderFactory.get(entityManager);

        for (IntelligenceFinding finding : findings) {
            document.add(new Paragraph("ENTRY ID: " + finding.getId(), sectionFont));
            document.add(new Paragraph("Source URL: " + finding.getSourceUrl(), normalFont));
            document.add(new Paragraph("Description: " + finding.getDescription(), normalFont));
            
            document.add(new Paragraph("--- DATABASE REVISION HISTORY (ENVERS) ---", auditFont));
            
            List<Number> revisions = auditReader.getRevisions(IntelligenceFinding.class, finding.getId());
            for (Number revNum : revisions) {
                AuditRevisionEntity revEntity = auditReader.findRevision(AuditRevisionEntity.class, revNum);
                IntelligenceFinding historical = auditReader.find(IntelligenceFinding.class, finding.getId(), revNum);
                
                document.add(new Paragraph(String.format("Revision: %s | Date: %s | Build: %s", 
                    revNum, revEntity.getRevisionDate(), revEntity.getCrawlerBuild()), auditFont));
                document.add(new Paragraph("Content Hash: " + revEntity.getDataHash(), auditFont));
                document.add(new Paragraph("Historical Content: " + historical.toString(), auditFont));
                document.add(new Paragraph(" "));
            }
            document.add(new Paragraph("\n"));
        }

        document.close();
        return out.toByteArray();
    }
}